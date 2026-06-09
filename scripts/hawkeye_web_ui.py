import streamlit as st
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path("c:/Users/prisc/Documents/Athena-Public")
PROJECTS_DIR = PROJECT_ROOT / "projects"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
REPORT_PATH = ARTIFACTS_DIR / "hawkeye_v5_audit_report.html"
REGIONS_PATH = PROJECT_ROOT / "vault" / "regulatory" / "nz_regions.json"

AUDIT_TIMEOUT_SECONDS = 120
REPORT_EMBED_HEIGHT = 800

st.set_page_config(page_title="Hawkeye Auditor", layout="wide")

def load_regions():
    """Load regional data for dropdowns."""
    if REGIONS_PATH.exists():
        with open(REGIONS_PATH, "r", encoding="utf-8") as f:
            try:
                return list(json.load(f).keys())
            except Exception:
                pass
    return []

def get_available_projects():
    """Scan for projects that have a configuration file."""
    projects = []
    if PROJECTS_DIR.exists():
        for d in PROJECTS_DIR.iterdir():
            if d.is_dir() and (d / "project_config.json").exists():
                projects.append(d.name)
    return projects

def render_sidebar(projects):
    """Render the sidebar and return the selected project."""
    st.sidebar.header("Projects")
    if not projects:
        st.sidebar.warning("No projects found.")
        return None
    return st.sidebar.selectbox("Select Project", projects)

def render_config_panel(selected_project_dir, regions):
    """Render the configuration editor for the selected project."""
    config_path = PROJECTS_DIR / selected_project_dir / "project_config.json"
    cfg = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception as e:
            st.error(f"Failed to load project config: {e}")
            return

    st.header(f"Configuration: {cfg.get('name', selected_project_dir)}")
    col1, col2 = st.columns(2)

    with col1:
        cfg["name"] = st.text_input("Project Name", cfg.get("name", ""))
        
        current_city = cfg.get("city", "")
        city_idx = regions.index(current_city) if current_city in regions else 0
        if regions:
            cfg["city"] = st.selectbox("City", regions, index=city_idx)
        else:
            cfg["city"] = st.text_input("City", current_city)
            
        wind_zones = ["Low", "Medium", "High", "Very High", "Extra High"]
        current_wind = cfg.get("wind_zone", "High")
        wind_idx = wind_zones.index(current_wind) if current_wind in wind_zones else 2
        cfg["wind_zone"] = st.selectbox("Wind Zone", wind_zones, index=wind_idx)
        
    with col2:
        foundation_types = ["Concrete Slab-on-Ground", "Timber Subfloor", "Suspended Concrete Slab", "slab"]
        current_found = cfg.get("foundation_type", "Concrete Slab-on-Ground")
        found_idx = foundation_types.index(current_found) if current_found in foundation_types else 0
        cfg["foundation_type"] = st.selectbox("Foundation Type", foundation_types, index=found_idx)
        
        cfg["is_alteration"] = st.checkbox("Is Alteration?", cfg.get("is_alteration", False))
        cfg["description"] = st.text_area("Description", cfg.get("description", ""))

    if st.button("Save Configuration"):
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            st.success("Configuration saved!")
        except Exception as e:
            st.error(f"Failed to save configuration: {e}")

def render_audit_runner():
    """Render the execution trigger and results."""
    st.divider()
    if st.button("Run Hawkeye Audit", type="primary"):
        st.info("Executing Hawkeye v5.0 compliance engine...")
        try:
            # Added timeout to prevent infinite hangs (Failure Mode Audit)
            result = subprocess.run(
                ["python", "scripts/hawkeye_v5_verify.py"], 
                cwd=str(PROJECT_ROOT), 
                capture_output=True, 
                text=True,
                timeout=AUDIT_TIMEOUT_SECONDS
            )
            st.code(result.stdout, language="text")
            if result.returncode == 0:
                st.success("Audit completed successfully.")
            else:
                st.error(f"Audit failed.\n{result.stderr}")
        except subprocess.TimeoutExpired:
            st.error("Audit timed out after 120 seconds. The process may be hanging.")
        except Exception as e:
            st.error(f"System error running audit: {e}")

def render_report():
    """Embed the generated HTML report."""
    st.divider()
    st.header("Audit Report")
    if REPORT_PATH.exists():
        try:
            with open(REPORT_PATH, "r", encoding="utf-8") as f:
                html_data = f.read()
            st.components.v1.html(html_data, height=REPORT_EMBED_HEIGHT, scrolling=True)
        except Exception as e:
            st.error(f"Failed to load HTML report: {e}")
    else:
        st.info("No audit report generated yet. Click 'Run Hawkeye Audit' above.")

def render_project_creation(regions):
    """Render the form to create a new project."""
    st.header("Create New Project")
    
    with st.form(key="new_project_form"):
        project_id = st.text_input("Project ID (e.g. project_alpha)").strip().lower()
        name = st.text_input("Project Name")
        
        city = st.selectbox("City", regions if regions else ["Unknown"])
        wind_zones = ["Low", "Medium", "High", "Very High", "Extra High"]
        wind_zone = st.selectbox("Wind Zone", wind_zones, index=2)
        
        foundation_types = ["Concrete Slab-on-Ground", "Timber Subfloor", "Suspended Concrete Slab", "slab"]
        foundation_type = st.selectbox("Foundation Type", foundation_types)
        
        is_alteration = st.checkbox("Is Alteration?", False)
        description = st.text_area("Description")
        
        submit = st.form_submit_button("Create Project")
        
    if submit:
        if not project_id:
            st.error("Project ID cannot be empty.")
            return
            
        project_dir = PROJECTS_DIR / project_id
        if project_dir.exists():
            st.error(f"Project directory '{project_id}' already exists!")
            return
            
        try:
            # Directive VII: Explicit Error Handling
            project_dir.mkdir(parents=True, exist_ok=False)
            
            cfg = {
                "id": project_id,
                "name": name,
                "city": city,
                "wind_zone": wind_zone,
                "foundation_type": foundation_type,
                "is_alteration": is_alteration,
                "description": description
            }
            
            config_path = project_dir / "project_config.json"
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
                
            st.success(f"Project {project_id} created successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Failed to create project: {e}")

def main():
    st.title("Hawkeye v5.0 Commercial Auditor")
    regions = load_regions()
    projects = get_available_projects()
    
    tab1, tab2 = st.tabs(["Audit Dashboard", "Create New Project"])
    
    with tab1:
        if not projects:
            st.warning("No projects found in projects/ directory. Go to 'Create New Project' to start.")
        else:
            selected_project = render_sidebar(projects)
            if selected_project:
                render_config_panel(selected_project, regions)
                render_audit_runner()
                render_report()
                
    with tab2:
        render_project_creation(regions)

if __name__ == "__main__":
    main()
