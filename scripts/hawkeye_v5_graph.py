#!/usr/bin/env python3
"""
Hawkeye v5.0 Cross-Document Fact Graph Builder
Builds a dependency graph connecting architectural sheets, engineering details,
and manufacturer specifications. Verifies cross-document alignment assertions.
"""

import os
import sys
import json
from pathlib import Path

class HawkeyeFactGraph:
    def __init__(self):
        # Nodes: id -> {type, metadata, properties}
        self.nodes = {}
        # Edges: (from_id, to_id) -> {type, description}
        self.edges = {}
        
    def add_node(self, node_id: str, node_type: str, properties: dict):
        self.nodes[node_id] = {
            "type": node_type,
            "properties": properties
        }
        
    def add_edge(self, from_id: str, to_id: str, edge_type: str, description: str = ""):
        self.edges[(from_id, to_id)] = {
            "type": edge_type,
            "description": description
        }
        
    def build_from_metadata(self, spec_data: dict, eng_data: dict, arch_data: dict):
        """
        Populate nodes and edges from parsed documents.
        """
        # Add project level node
        self.add_node("project", "metadata", {
            "wind_zone": eng_data.get("wind_zone", "unknown"),
            "exposure_zone": eng_data.get("exposure_zone", "unknown"),
            "seismic_zone": eng_data.get("seismic_zone", "unknown")
        })
        
        # Add Specification Nodes
        for section, spec in spec_data.items():
            spec_id = f"spec_{section}"
            self.add_node(spec_id, "specification", {
                "section": section,
                "product_name": spec.get("product_name"),
                "manufacturer": spec.get("manufacturer"),
                "min_thickness": spec.get("min_thickness"),
                "slope_req": spec.get("slope_req")
            })
            self.add_edge("project", spec_id, "governs", f"Spec section for {section}")
            
        # Add Engineering Nodes
        for detail_name, detail in eng_data.get("details", {}).items():
            eng_id = f"eng_{detail_name}"
            self.add_node(eng_id, "engineering", {
                "name": detail_name,
                "dimension": detail.get("dimension"),
                "material": detail.get("material"),
                "fixing": detail.get("fixing")
            })
            self.add_edge("project", eng_id, "engineered_spec", f"Engineer spec for {detail_name}")
            
        # Add Architectural Drawing Nodes
        for sheet_num, sheet in arch_data.items():
            sheet_id = f"arch_sheet_{sheet_num}"
            self.add_node(sheet_id, "architectural_drawing", {
                "sheet_num": sheet_num,
                "title": sheet.get("title"),
                "dimensions": sheet.get("dimensions", {}),
                "notes": sheet.get("notes", [])
            })
            
            # Map calls / references from drawings to spec or engineer detail
            for ref in sheet.get("references", []):
                # Try to link to engineering
                for eng_id in self.nodes:
                    if self.nodes[eng_id]["type"] == "engineering" and ref.lower() in eng_id.lower():
                        self.add_edge(sheet_id, eng_id, "references", f"Links drawing to engineering details")
                # Try to link to spec
                for spec_id in self.nodes:
                    if self.nodes[spec_id]["type"] == "specification" and ref.lower() in self.nodes[spec_id]["properties"]["product_name"].lower():
                        self.add_edge(sheet_id, spec_id, "specifies", f"Links drawing element to manufacturer specs")
                        
    def run_assertions(self):
        """
        Audits the graph and returns RFI hazards.
        """
        discrepancies = []
        
        # Assertion 1: Lintel & Structural matches
        for from_id, to_id in self.edges:
            edge = self.edges[(from_id, to_id)]
            if edge["type"] == "references":
                arch_node = self.nodes[from_id]
                eng_node = self.nodes[to_id]
                
                # Check dimensional or material conflict
                arch_dims = arch_node["properties"].get("dimensions", {})
                eng_dims = eng_node["properties"].get("dimension")
                
                # Compare dimensions if present
                for key, val in arch_dims.items():
                    if eng_dims and key in eng_node["properties"]["name"].lower():
                        if str(val) != str(eng_dims):
                            discrepancies.append({
                                "severity": "CRITICAL",
                                "category": "B1 Structure",
                                "message": f"Dimension mismatch on {from_id} for '{key}': Arch shows '{val}' but Eng specifies '{eng_dims}'."
                            })
                            
        # Assertion 2: Specifications Match Drawings
        for from_id, to_id in self.edges:
            edge = self.edges[(from_id, to_id)]
            if edge["type"] == "specifies":
                arch_node = self.nodes[from_id]
                spec_node = self.nodes[to_id]
                
                # Compare waterproofing/membrane slope requirement
                for note in arch_node["properties"].get("notes", []):
                    if "slope" in note.lower() or "fall" in note.lower():
                        spec_slope = spec_node["properties"].get("slope_req")
                        if spec_slope and spec_slope not in note:
                            discrepancies.append({
                                "severity": "MEDIUM",
                                "category": "E2 Weathertightness",
                                "message": f"Slope requirement contradiction: Spec Section '{spec_node['properties']['section']}' requires '{spec_slope}' slope, but Drawing '{arch_node['properties']['sheet_num']}' notes: '{note}'"
                            })
                            
        return discrepancies

if __name__ == "__main__":
    # Test data
    test_spec = {
        "0421": {"product_name": "Ardex WPM 195", "manufacturer": "Ardex", "slope_req": "1.5 deg"},
        "0431": {"product_name": "Viking Roofspec", "manufacturer": "Viking", "slope_req": "2.0 deg"}
    }
    test_eng = {
        "wind_zone": "High",
        "details": {
            "lintel_garage": {"dimension": "200PFC", "material": "Steel"},
            "footing_depth": {"dimension": "600", "material": "Concrete"}
        }
    }
    test_arch = {
        "301": {
            "title": "Foundation Plan",
            "dimensions": {"footing_depth": 300},
            "notes": ["Refer to engineering for structural footing sizing"],
            "references": ["footing_depth"]
        },
        "702": {
            "title": "Deck Detail",
            "dimensions": {},
            "notes": ["Provide membrane with 1.0 deg fall"],
            "references": ["Ardex WPM 195"]
        }
    }
    
    graph = HawkeyeFactGraph()
    graph.build_from_metadata(test_spec, test_eng, test_arch)
    rfi_risks = graph.run_assertions()
    
    print("\n--- Graph Auditor RFI Risks ---")
    for risk in rfi_risks:
        print(f"[{risk['severity']}] {risk['category']}: {risk['message']}")
