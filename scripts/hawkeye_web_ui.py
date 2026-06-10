import streamlit as st
import json
import re
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
    selected = st.sidebar.selectbox("Select Project", projects)
    
    st.sidebar.divider()
    st.sidebar.markdown("### Danger Zone")
    with st.sidebar.expander("Delete Project"):
        st.warning("This will permanently delete the project and all associated files.")
        if st.button("Confirm Delete"):
            success = False
            try:
                target_dir = PROJECTS_DIR / selected
                if target_dir.exists():
                    import shutil
                    shutil.rmtree(target_dir)
                    success = True
            except Exception as e:
                st.error(f"Failed to delete: {e}")
            if success:
                st.rerun()
        
    return selected

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
    col1, col2, col3 = st.columns(3)

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

    with col3:
        cfg["length"] = st.number_input("Building Length (m)", value=float(cfg.get("length", 0.0)), step=0.1)
        cfg["width"] = st.number_input("Building Width (m)", value=float(cfg.get("width", 0.0)), step=0.1)
        cfg["roof_pitch"] = st.number_input("Roof Pitch (°)", value=float(cfg.get("roof_pitch", 0.0)), step=1.0)

    st.divider()
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        if st.button("💾 Save Configuration", use_container_width=True, type="primary"):
            try:
                if config_path.exists():
                    import shutil
                    original_path = config_path.with_name("project_config.original.json")
                    if not original_path.exists():
                        shutil.copy2(config_path, original_path)
                    backup_path = config_path.with_name(config_path.name + ".bak")
                    shutil.copy2(config_path, backup_path)
                    
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, indent=2)
                st.success("Configuration saved! (Baseline locked & version backed up)")
            except Exception as e:
                st.error(f"Failed to save configuration: {e}")

    with col_s2:
        undo_clicked = st.button("⏪ Undo Last Save", use_container_width=True)

    with col_s3:
        restore_clicked = st.button("⏮️ Restore Baseline", use_container_width=True)
        
    if undo_clicked:
        backup_path = config_path.with_name(config_path.name + ".bak")
        if backup_path.exists():
            import shutil
            shutil.copy2(backup_path, config_path)
            st.rerun()
        else:
            st.warning("No previous save found.")
            
    if restore_clicked:
        original_path = config_path.with_name("project_config.original.json")
        if original_path.exists():
            import shutil
            shutil.copy2(original_path, config_path)
            st.rerun()
        else:
            st.warning("No baseline found.")

def render_file_upload(selected_project_dir):
    """Render a file uploader to accept building plans."""
    st.divider()
    st.header("Upload Building Plans")
    
    project_path = PROJECTS_DIR / selected_project_dir
    if project_path.exists():
        existing_files = [f for f in project_path.iterdir() if f.is_file() and f.name.endswith(".pdf")]
        if existing_files:
            st.write("**Currently Uploaded Plans:**")
            for f in existing_files:
                col_f1, col_f2 = st.columns([0.9, 0.1])
                with col_f1:
                    st.text(f"📄 {f.name}")
                with col_f2:
                    if st.button("❌", key=f"del_{f.name}"):
                        f.unlink()
                        st.rerun()
                        
            if st.button("🗑️ Clear All PDF Plans"):
                for f in existing_files:
                    f.unlink()
                st.rerun()
        else:
            st.info("No plans uploaded yet.")
            
    uploaded_files = st.file_uploader("Upload New PDF Plans", type=["pdf"], accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            file_path = PROJECTS_DIR / selected_project_dir / Path(file.name).name
            if not file_path.exists():
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
                st.success(f"File '{file.name}' saved successfully!")
            else:
                st.warning(f"File '{file.name}' already exists. Skipping.")

def render_audit_runner(selected_project_dir):
    """Render the execution trigger and results."""
    st.divider()
    if st.button("Run Hawkeye Audit", type="primary"):
        with st.spinner("Executing Hawkeye v5.0 compliance engine (this may take up to 2 minutes)..."):
            try:
                # Added timeout to prevent infinite hangs (Failure Mode Audit)
                result = subprocess.run(
                    ["python", "scripts/hawkeye_v5_verify.py", "--project", selected_project_dir], 
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
        project_id_raw = st.text_input("Project ID (e.g. project_alpha)").strip().lower().replace(" ", "_")
        project_id = re.sub(r'[^a-z0-9_]', '', project_id_raw)
        name = st.text_input("Project Name")
        
        city = st.selectbox("City", regions if regions else ["Unknown"])
        wind_zones = ["Low", "Medium", "High", "Very High", "Extra High"]
        wind_zone = st.selectbox("Wind Zone", wind_zones, index=2)
        
        foundation_types = ["Concrete Slab-on-Ground", "Timber Subfloor", "Suspended Concrete Slab", "slab"]
        foundation_type = st.selectbox("Foundation Type", foundation_types)
        
        dim_col1, dim_col2, dim_col3 = st.columns(3)
        with dim_col1:
            length = st.number_input("Building Length (m)", value=0.0, step=0.1)
        with dim_col2:
            width = st.number_input("Building Width (m)", value=0.0, step=0.1)
        with dim_col3:
            roof_pitch = st.number_input("Roof Pitch (°)", value=0.0, step=1.0)
        
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
                "length": length,
                "width": width,
                "roof_pitch": roof_pitch,
                "is_alteration": is_alteration,
                "description": description
            }
            
            config_path = project_dir / "project_config.json"
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
                
            st.success(f"Project {project_id} created successfully!")
            
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
                render_file_upload(selected_project)
                render_audit_runner(selected_project)
                render_report()
                
    with tab2:
        render_project_creation(regions)

if __name__ == "__main__":
    main()
