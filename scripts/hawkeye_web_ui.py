import streamlit as st
import json
import os
import sys
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path("c:/Users/prisc/Documents/Athena-Public")
PROJECTS_DIR = PROJECT_ROOT / "projects"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
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
        del_submit = st.button("Confirm Delete")
        st.caption("Wipes all PDFs, configurations, and reports from the local drive.")
        if del_submit:
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

def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

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
        
        wall_claddings = ["Light", "Medium", "Heavy"]
        current_wall_clad = str(cfg.get("wall_cladding", "Light")).capitalize()
        wall_clad_idx = wall_claddings.index(current_wall_clad) if current_wall_clad in wall_claddings else 0
        cfg["wall_cladding"] = st.selectbox("Wall Cladding", wall_claddings, index=wall_clad_idx)

        roof_claddings = ["Light", "Heavy"]
        current_roof_clad = str(cfg.get("roof_cladding", "Light")).capitalize()
        roof_clad_idx = roof_claddings.index(current_roof_clad) if current_roof_clad in roof_claddings else 0
        cfg["roof_cladding"] = st.selectbox("Roof Cladding", roof_claddings, index=roof_clad_idx)
        
        cfg["is_alteration"] = st.checkbox("Is Alteration?", cfg.get("is_alteration", False))
        cfg["description"] = st.text_area("Description", cfg.get("description", ""))

    with col3:
        cfg["length"] = st.number_input("Building Length (m)", value=safe_float(cfg.get("length", 0.0)), step=0.1, min_value=0.0)
        cfg["width"] = st.number_input("Building Width (m)", value=safe_float(cfg.get("width", 0.0)), step=0.1, min_value=0.0)
        cfg["wall_height"] = st.number_input("Wall Height (m)", value=safe_float(cfg.get("wall_height", 2.4)), step=0.1, min_value=0.0)
        cfg["roof_pitch"] = st.number_input("Roof Pitch (°)", value=safe_float(cfg.get("roof_pitch", 0.0)), step=1.0, min_value=0.0, max_value=90.0)

    st.divider()
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        save_btn = st.button("💾 Save Configuration", use_container_width=True, type="primary")
        st.caption("Locks in configuration changes and creates an automatic rollback backup.")
        if save_btn:
            try:
                if config_path.exists():
                    import shutil
                    original_path = config_path.with_name("project_config.original.json")
                    if not original_path.exists():
                        shutil.copy2(config_path, original_path)
                    backup_path = config_path.with_name(config_path.name + ".bak")
                    shutil.copy2(config_path, backup_path)
                    
                tmp_path = config_path.with_suffix('.json.tmp')
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, indent=2)
                os.replace(tmp_path, config_path)
                st.success("Configuration saved! (Baseline locked & version backed up)")
            except Exception as e:
                st.error(f"Failed to save configuration: {e}")

    with col_s2:
        undo_clicked = st.button("⏪ Undo Last Save", use_container_width=True)
        st.caption("Reverts the configuration to the state it was in before your last save.")

    with col_s3:
        restore_clicked = st.button("⏮️ Restore Baseline", use_container_width=True)
        st.caption("Reverts the configuration to the original state from project creation.")
        
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
                        try:
                            f.unlink()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete '{f.name}': {e}")
                        
            if st.button("🗑️ Clear All PDF Plans"):
                st.session_state[f"confirm_clear_{selected_project_dir}"] = True
            st.caption("Instantly purges all uploaded PDFs from the project directory.")
            
            if st.session_state.get(f"confirm_clear_{selected_project_dir}", False):
                st.warning("Are you sure you want to permanently delete all uploaded PDFs?")
                c_yes, c_no = st.columns(2)
                with c_yes:
                    if st.button("✅ Yes, Delete All", type="primary"):
                        for f in existing_files:
                            try:
                                f.unlink()
                            except Exception as e:
                                st.error(f"Failed to delete '{f.name}': {e}")
                        st.session_state[f"confirm_clear_{selected_project_dir}"] = False
                        st.rerun()
                with c_no:
                    if st.button("❌ No, Cancel"):
                        st.session_state[f"confirm_clear_{selected_project_dir}"] = False
                        st.rerun()
        else:
            st.info("No plans uploaded yet.")
            
    uploaded_files = st.file_uploader("Upload New PDF Plans", type=["pdf"], accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            file_path = PROJECTS_DIR / selected_project_dir / Path(file.name).name
            if not file_path.exists():
                try:
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    st.success(f"File '{file.name}' saved successfully!")
                except Exception as e:
                    st.error(f"Failed to save '{file.name}': {e}")
            else:
                st.warning(f"File '{file.name}' already exists. Skipping.")

def render_audit_runner(selected_project_dir):
    """Render the execution trigger and results."""
    st.divider()
    audit_btn = st.button("🚀 Run Hawkeye Audit", type="primary", use_container_width=True)
    st.caption("Executes the local compliance engine against the current configuration and PDFs. Takes ~5-15 seconds depending on document size.")
    if audit_btn:
        with st.spinner("Executing Hawkeye v5.0 compliance engine (this may take up to 2 minutes)..."):
            try:
                # Added timeout to prevent infinite hangs (Failure Mode Audit)
                result = subprocess.run(
                    [sys.executable, "scripts/hawkeye_v5_verify.py", "--project", selected_project_dir], 
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

def render_report(selected_project_dir):
    """Embed the generated HTML report."""
    st.divider()
    st.header("Audit Report")
    report_path = ARTIFACTS_DIR / f"hawkeye_report_{selected_project_dir}.html"
    if report_path.exists():
        try:
            mtime = os.path.getmtime(report_path)
            from datetime import datetime
            last_run = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            st.caption(f"⏱️ **Last Audited:** {last_run}")
            
            with open(report_path, "r", encoding="utf-8") as f:
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
        
        clad_col1, clad_col2 = st.columns(2)
        with clad_col1:
            wall_cladding = st.selectbox("Wall Cladding Weight", ["Light", "Medium", "Heavy"])
        with clad_col2:
            roof_cladding = st.selectbox("Roof Cladding Weight", ["Light", "Heavy"])
        
        dim_col1, dim_col2, dim_col3, dim_col4 = st.columns(4)
        with dim_col1:
            length = st.number_input("Building Length (m)", value=0.0, step=0.1, min_value=0.0)
        with dim_col2:
            width = st.number_input("Building Width (m)", value=0.0, step=0.1, min_value=0.0)
        with dim_col3:
            wall_height = st.number_input("Wall Height (m)", value=2.4, step=0.1, min_value=0.0)
        with dim_col4:
            roof_pitch = st.number_input("Roof Pitch (°)", value=0.0, step=1.0, min_value=0.0, max_value=90.0)
        
        is_alteration = st.checkbox("Is Alteration?", False)
        description = st.text_area("Description")
        
        submit = st.form_submit_button("Create Project")
        st.caption("Initializes a new secure project workspace. ID must be unique.")
        
    if submit:
        if not project_id:
            st.error("Project ID cannot be empty.")
            return
            
        reserved_ids = ["portobello", "lynn_street", "bedford_parade"]
        if project_id in reserved_ids:
            st.error(f"Project ID '{project_id}' is a reserved legacy namespace. Please choose a different ID.")
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
                "wall_cladding": wall_cladding,
                "roof_cladding": roof_cladding,
                "length": length,
                "width": width,
                "wall_height": wall_height,
                "roof_pitch": roof_pitch,
                "is_alteration": is_alteration,
                "description": description
            }
            
            config_path = project_dir / "project_config.json"
            tmp_path = config_path.with_suffix('.json.tmp')
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            os.replace(tmp_path, config_path)
                
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
                render_report(selected_project)
                
    with tab2:
        render_project_creation(regions)

if __name__ == "__main__":
    main()
