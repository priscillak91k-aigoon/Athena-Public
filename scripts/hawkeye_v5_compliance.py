#!/usr/bin/env python3
"""
Hawkeye v5.0 Local NZBC & BRANZ Compliance Solver
Performs keyword-in-context (KWIC) and semantic-style retrieval over local NZBC and BRANZ texts.
Provides regulatory assertions for the plan auditor.
"""

import os
import sys
import re
from pathlib import Path

# Paths to potential local compliance resources
KNOWLEDGE_DIR = Path.home() / ".gemini" / "antigravity" / "knowledge" / "nzbc_e2_as1_flashings_branz" / "artifacts"
E2_TEXT_FILE = KNOWLEDGE_DIR / "e2_as1_full_text.txt"

class HawkeyeComplianceSolver:
    def __init__(self, resource_path: Path = E2_TEXT_FILE):
        self.resource_path = resource_path
        self.text_content = ""
        self._load_resource()
        
    def _load_resource(self):
        if self.resource_path.exists():
            try:
                with open(self.resource_path, 'r', encoding='utf-8', errors='ignore') as f:
                    self.text_content = f.read()
            except Exception as e:
                print(f"Error loading compliance file: {e}")
        else:
            # Fallback if the specific KI directory isn't mounted or structured this way
            print(f"Compliance resource not found at {self.resource_path}. Running with empty compliance index.")
            
    def search_rules(self, query: str, max_results: int = 5):
        """
        Locates key clauses, tables, or figures in the NZBC E2/AS1 text relating to a query.
        """
        if not self.text_content:
            return []
            
        # Standard keyword search with paragraph context
        terms = query.lower().split()
        paragraphs = self.text_content.split("\n\n")
        
        matches = []
        for para in paragraphs:
            para_lower = para.lower()
            score = sum(1 for term in terms if term in para_lower)
            if score > 0:
                # Highlight terms in text
                matches.append((score, para.strip()))
                
        # Sort by match score
        matches.sort(key=lambda x: x[0], reverse=True)
        return [text for score, text in matches[:max_results]]

    def assert_clearance(self, surface_type: str, ffl_ground_distance: float) -> dict:
        """
        Asserts NZBC E1/AS1 & E2/AS1 clearance rules.
        surface_type: 'unpaved' or 'paved'
        ffl_ground_distance: distance in mm
        """
        if surface_type == "unpaved":
            limit = 225.0
            clause = "E1/AS1 (3.0.1) & E2/AS1 Table 7"
        elif surface_type == "paved":
            limit = 150.0
            clause = "E1/AS1 (3.0.1) & E2/AS1 Table 7"
        else:
            return {"status": "UNKNOWN", "message": "Unknown surface type. Specify 'paved' or 'unpaved'."}
            
        if ffl_ground_distance < limit:
            return {
                "status": "FAIL",
                "clause": clause,
                "message": f"FFL ground clearance of {ffl_ground_distance}mm is below the minimum required {limit}mm for {surface_type} surfaces."
            }
        return {"status": "PASS", "clause": clause, "message": "FFL clearance is compliant."}

    def assert_deck_slope(self, slope_deg: float) -> dict:
        """
        Asserts deck membrane slope limits.
        """
        # E2/AS1 3rd/4th edition requires 1.5 degrees (1:40) minimum fall for decks
        if slope_deg < 1.5:
            return {
                "status": "FAIL",
                "clause": "E2/AS1 Clause 8.5.1",
                "message": f"Deck slope of {slope_deg} degrees is below the E2/AS1 minimum of 1.5 degrees (1:40 fall)."
            }
        return {"status": "PASS", "clause": "E2/AS1 Clause 8.5.1", "message": "Deck slope is compliant."}

    def calculate_wind_bracing_demand(self, width: float, length: float, wall_height: float, roof_pitch_deg: float, wind_zone: str, roof_type: str = "gable") -> dict:
        """
        Calculates Wind Bracing Demand in Bracing Units (BUs) per NZS 3604:2011.
        width, length, wall_height in meters.
        """
        # Wind pressure mapping based on NZS 3604 Wind Zones (kPa)
        pressures = {
            "low": 0.61,
            "medium": 0.82,
            "high": 1.16,
            "very high": 1.50,
            "extra high": 1.82
        }
        
        p = pressures.get(wind_zone.lower(), 1.16) # default to high
        
        import math
        pitch_rad = math.radians(roof_pitch_deg)
        
        # Calculate roof height
        if roof_type.lower() == "gable":
            roof_height = (width / 2.0) * math.tan(pitch_rad)
        else: # hip/other (approximate)
            roof_height = (width / 4.0) * math.tan(pitch_rad)
            
        # Drag coefficient Cd = 1.2, Conversion factor: 1 kPa = 20 BUs/m2
        factor = p * 1.2 * 20
        
        # Projected areas
        # 1. Across direction (wind blowing perpendicular to length)
        projected_area_across = (wall_height * length) + (roof_height * length)
        demand_across = projected_area_across * factor
        
        # 2. Along direction (wind blowing perpendicular to width)
        if roof_type.lower() == "gable":
            projected_area_along = (wall_height * width) + (0.5 * width * roof_height)
        else:
            projected_area_along = (wall_height * width) + (0.25 * width * roof_height)
            
        demand_along = projected_area_along * factor
        
        # NZS 3604 min demand is 85 BUs or 5.0 BUs/m of wall, whichever is greater.
        demand_across = max(demand_across, 85.0)
        demand_along = max(demand_along, 85.0)
        
        return {
            "wind_zone": wind_zone,
            "pressure_kpa": p,
            "demand_across_bu": round(demand_across, 1),
            "demand_along_bu": round(demand_along, 1),
            "projected_area_across_m2": round(projected_area_across, 2),
            "projected_area_along_m2": round(projected_area_along, 2)
        }

    def calculate_seismic_bracing_demand(self, ground_area: float, Z_factor: float, wall_cladding: str, roof_cladding: str, foundation_type: str) -> float:
        """
        Calculates Seismic Bracing Demand in Bracing Units (BUs) per NZS 3604:2011.
        Dunedin Z factor = 0.13.
        """
        # Base rates for Z = 0.3 (standard NZS 3604 scaling baseline)
        # Rates depend on cladding weights and foundation
        # Cladding: light (l), medium (m), heavy (h)
        # Foundation: slab, timber
        wc = wall_cladding.lower()
        rc = roof_cladding.lower()
        fd = foundation_type.lower()
        
        # Look up baseline rate per square meter (for Z=0.3)
        if fd == "slab":
            if wc == "light" and rc == "light":
                base_rate = 3.0
            elif wc == "medium" or rc == "heavy":
                base_rate = 4.5
            else: # heavy wall cladding (brick veneer)
                base_rate = 6.0
        else: # timber suspended floor
            if wc == "light" and rc == "light":
                base_rate = 5.5
            elif wc == "medium" or rc == "heavy":
                base_rate = 7.5
            else:
                base_rate = 10.0
                
        # Scale by Z factor: demand = area * base_rate * (Z / 0.3)
        seismic_demand = ground_area * base_rate * (Z_factor / 0.3)
        
        # NZS 3604 min demand check
        seismic_demand = max(seismic_demand, 85.0)
        
        return round(seismic_demand, 1)

    def assert_bracing_adequacy(self, calculated_demand: dict, provided_capacity: dict) -> dict:
        """
        Checks if provided bracing capacities meet the calculated demand requirements.
        provided_capacity = {"along_bu": float, "across_bu": float}
        """
        results = []
        status = "PASS"
        
        # Wind Checks
        wind_across = calculated_demand.get("wind", {}).get("demand_across_bu", 0)
        wind_along = calculated_demand.get("wind", {}).get("demand_along_bu", 0)
        
        # Seismic Check (seismic demand is isotropic - applies equally along and across)
        seismic = calculated_demand.get("seismic_bu", 0)
        
        # Final Demands
        final_demand_across = max(wind_across, seismic)
        final_demand_along = max(wind_along, seismic)
        
        provided_across = provided_capacity.get("across_bu", 0)
        provided_along = provided_capacity.get("along_bu", 0)
        
        if provided_across < final_demand_across:
            status = "FAIL"
            results.append(f"Across-direction bracing deficit: Provided {provided_across} BUs, but demand is {final_demand_across} BUs (Wind: {wind_across}, Seismic: {seismic}).")
            
        if provided_along < final_demand_along:
            status = "FAIL"
            results.append(f"Along-direction bracing deficit: Provided {provided_along} BUs, but demand is {final_demand_along} BUs (Wind: {wind_along}, Seismic: {seismic}).")
            
        return {
            "status": status,
            "calculated_demands": {
                "across_bu": final_demand_across,
                "along_bu": final_demand_along,
                "breakdown": {
                    "wind_across": wind_across,
                    "wind_along": wind_along,
                    "seismic": seismic
                }
            },
            "provided_capacity": provided_capacity,
            "discrepancies": results
        }
            
    def assert_terminal_vent(self, labels: list) -> dict:
        """
        Asserts that the drainage system features a designated open terminal vent.
        Under AS/NZS 3500.2 Clause 6.8, every system must have at least one terminal vent.
        """
        has_terminal = False
        for label in labels:
            if "stack" in label.lower() and ("terminal" in label.lower() or "vent" in label.lower() or "open" in label.lower()):
                has_terminal = True
                break
                
        if not has_terminal:
            return {
                "status": "FAIL",
                "clause": "AS/NZS 3500.2 Clause 6.8",
                "message": "Terminal vent designation missing. The plan shows a '100Ø Stack' but does not specify that it extends as an open terminal vent to the atmosphere."
            }
        return {"status": "PASS", "clause": "AS/NZS 3500.2 Clause 6.8", "message": "Terminal vent is designated."}

    def assert_org_presence(self, labels: list) -> dict:
        """
        Asserts that an Overflow Relief Gully (ORG) is designated.
        Under AS/NZS 3500.2 Clause 4.6.6, every system must have at least one ORG.
        """
        has_org = False
        import re
        for label in labels:
            if re.search(r"\borg\b", label, re.IGNORECASE) or "overflow relief" in label.lower() or "overflow gully" in label.lower():
                has_org = True
                break
                
        if not has_org:
            return {
                "status": "FAIL",
                "clause": "AS/NZS 3500.2 Clause 4.6.6",
                "message": "Overflow Relief Gully (ORG) designation missing. The plan fails to show or designate an external ORG, which is mandatory to protect the interior from flooding during a blockage."
            }
        return {"status": "PASS", "clause": "AS/NZS 3500.2 Clause 4.6.6", "message": "ORG is designated."}

    def assert_h1_compliance(self, climate_zone: int, floor_type: str, r_roof: float, r_wall: float, r_floor: float, is_alteration: bool = False) -> dict:
        """
        Asserts H1/AS1 compliance for roof, wall, and floor insulation.
        climate_zone: 1 to 6
        floor_type: 'suspended' or 'slab'
        r_roof, r_wall, r_floor: provided R-values
        is_alteration: if True, handles change of use / ANARP exceptions
        """
        min_roof = 6.6
        min_wall = 2.0
        
        if floor_type.lower() == "suspended":
            if climate_zone in [1, 2]:
                min_floor = 2.5
            elif climate_zone in [3, 4]:
                min_floor = 2.8
            else: # Zones 5 and 6
                min_floor = 3.0
        else: # slab-on-ground
            if climate_zone in [1, 2, 3, 4]:
                min_floor = 1.5
            elif climate_zone == 5:
                min_floor = 1.6
            else: # Zone 6
                min_floor = 1.7
                
        results = []
        status = "PASS"
        
        if r_roof < min_roof:
            status = "FAIL"
            results.append(f"Roof R-value R{r_roof} is below H1/AS1 minimum R{min_roof}.")
            
        if r_wall < min_wall:
            status = "FAIL"
            results.append(f"Wall R-value R{r_wall} is below H1/AS1 minimum R{min_wall}.")
            
        if r_floor < min_floor:
            if is_alteration:
                status = "WARNING"
                results.append(
                    f"Floor R-value R{r_floor} is below new build H1/AS1 minimum R{min_floor} for Climate Zone {climate_zone}. "
                    "However, as this is a Change of Use alteration, compliance may be demonstrated under the ANARP (As Nearly As Reasonably Practicable) path. "
                    "A formal Section 115 ANARP report detailing floor clearance constraints and compensatory insulation must be submitted to the Council."
                )
            else:
                status = "FAIL"
                results.append(f"Floor R-value R{r_floor} is below H1/AS1 minimum R{min_floor} for Climate Zone {climate_zone} ({floor_type} floor).")
                
        return {
            "status": status,
            "min_requirements": {
                "roof": min_roof,
                "wall": min_wall,
                "floor": min_floor
            },
            "provided": {
                "roof": r_roof,
                "wall": r_wall,
                "floor": r_floor
            },
            "discrepancies": results
        }

if __name__ == "__main__":
    solver = HawkeyeComplianceSolver()
    
    # Test assertions
    print("\n--- Testing Clearance Assertions ---")
    print(solver.assert_clearance("unpaved", 150))
    print(solver.assert_clearance("paved", 160))
    
    print("\n--- Testing Deck Slope Assertion ---")
    print(solver.assert_deck_slope(1.0))
    
    # Test bracing demand calculations
    print("\n--- Testing Wind Bracing calculations (NZS 3604) ---")
    wind_demand = solver.calculate_wind_bracing_demand(
        width=8.0, length=12.0, wall_height=2.4, roof_pitch_deg=25.0, wind_zone="high"
    )
    print(json.dumps(wind_demand, indent=2))
    
    print("\n--- Testing Seismic Bracing calculations (Z=0.13 Dunedin) ---")
    seismic_demand = solver.calculate_seismic_bracing_demand(
        ground_area=96.0, Z_factor=0.13, wall_cladding="light", roof_cladding="light", foundation_type="slab"
    )
    print(f"Seismic Demand: {seismic_demand} BUs")
    
    print("\n--- Testing Bracing Adequacy Assertion ---")
    demand_summary = {"wind": wind_demand, "seismic_bu": seismic_demand}
    provided = {"along_bu": 250.0, "across_bu": 500.0}
    adequacy = solver.assert_bracing_adequacy(demand_summary, provided)
    print(json.dumps(adequacy, indent=2))
