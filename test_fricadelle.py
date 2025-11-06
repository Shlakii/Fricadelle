#!/usr/bin/env python3
"""
Tests unitaires pour les composants de Fricadelle.
"""

import json
import unittest
from vulnerability_schema import validate_vulnerability_response, get_cvss_guidance


class TestVulnerabilitySchema(unittest.TestCase):
    """Tests pour le module de validation de schéma"""
    
    def test_valid_response(self):
        """Test avec une réponse valide"""
        response = {
            "vulnerabilities": [
                {
                    "title": "Test Vulnerability with Valid Length",
                    "severity": "high",
                    "cvss_score": 7.5,
                    "cve_ids": ["CVE-2024-1234"],
                    "finding_type": "Configuration Error",
                    "description": "This is a detailed description of the vulnerability that is long enough to pass validation.",
                    "remediation": "This is a detailed remediation plan that is long enough to pass validation.",
                    "business_impact": "This describes the business impact of the vulnerability.",
                    "affected_assets": ["server1.example.com"],
                    "evidence": "Technical evidence of the vulnerability"
                }
            ]
        }
        
        is_valid, error = validate_vulnerability_response(response)
        self.assertTrue(is_valid, f"Validation failed: {error}")
        self.assertIsNone(error)
    
    def test_empty_vulnerabilities(self):
        """Test avec liste de vulnérabilités vide (valide)"""
        response = {"vulnerabilities": []}
        is_valid, error = validate_vulnerability_response(response)
        self.assertTrue(is_valid, f"Empty list should be valid: {error}")
    
    def test_missing_vulnerabilities_key(self):
        """Test sans clé vulnerabilities (invalide)"""
        response = {"findings": []}
        is_valid, error = validate_vulnerability_response(response)
        self.assertFalse(is_valid)
        self.assertIn("vulnerabilities", error)
    
    def test_invalid_severity(self):
        """Test avec sévérité invalide"""
        response = {
            "vulnerabilities": [
                {
                    "title": "Test Vulnerability with Valid Length",
                    "severity": "super_critical",  # Invalid
                    "cvss_score": 7.5,
                    "cve_ids": [],
                    "finding_type": "Test",
                    "description": "Long enough description to pass minimum length validation requirements.",
                    "remediation": "Long enough remediation to pass minimum length validation requirements.",
                    "business_impact": "Long enough business impact description.",
                    "affected_assets": ["test"],
                    "evidence": "Test evidence"
                }
            ]
        }
        
        is_valid, error = validate_vulnerability_response(response)
        self.assertFalse(is_valid)
        self.assertIn("severity", error.lower())
    
    def test_invalid_cvss_score(self):
        """Test avec score CVSS invalide"""
        response = {
            "vulnerabilities": [
                {
                    "title": "Test Vulnerability with Valid Length",
                    "severity": "high",
                    "cvss_score": 15.0,  # Invalid (max is 10.0)
                    "cve_ids": [],
                    "finding_type": "Test",
                    "description": "Long enough description to pass minimum length validation requirements.",
                    "remediation": "Long enough remediation to pass minimum length validation requirements.",
                    "business_impact": "Long enough business impact description.",
                    "affected_assets": ["test"],
                    "evidence": "Test evidence"
                }
            ]
        }
        
        is_valid, error = validate_vulnerability_response(response)
        self.assertFalse(is_valid)
        self.assertIn("cvss", error.lower())
    
    def test_missing_required_field(self):
        """Test avec champ requis manquant"""
        response = {
            "vulnerabilities": [
                {
                    "title": "Test Vulnerability",
                    "severity": "high",
                    # Missing cvss_score
                    "finding_type": "Test",
                    "description": "Description",
                    "remediation": "Remediation",
                    "business_impact": "Impact",
                    "affected_assets": ["test"],
                    "evidence": "Evidence"
                }
            ]
        }
        
        is_valid, error = validate_vulnerability_response(response)
        self.assertFalse(is_valid)
        self.assertIn("cvss_score", error)
    
    def test_description_too_short(self):
        """Test avec description trop courte"""
        response = {
            "vulnerabilities": [
                {
                    "title": "Test Vulnerability with Valid Length",
                    "severity": "high",
                    "cvss_score": 7.5,
                    "cve_ids": [],
                    "finding_type": "Test",
                    "description": "Short",  # Too short
                    "remediation": "Long enough remediation to pass minimum length validation requirements.",
                    "business_impact": "Long enough business impact description.",
                    "affected_assets": ["test"],
                    "evidence": "Test evidence"
                }
            ]
        }
        
        is_valid, error = validate_vulnerability_response(response)
        self.assertFalse(is_valid)
        self.assertIn("description", error.lower())
    
    def test_cvss_guidance(self):
        """Test de la guidance CVSS"""
        critical = get_cvss_guidance("critical")
        self.assertIn("9.0-10.0", critical)
        
        high = get_cvss_guidance("high")
        self.assertIn("7.0-8.9", high)
        
        medium = get_cvss_guidance("medium")
        self.assertIn("4.0-6.9", medium)
        
        low = get_cvss_guidance("low")
        self.assertIn("0.1-3.9", low)


class TestDataStructures(unittest.TestCase):
    """Tests pour les structures de données"""
    
    def test_findings_structure(self):
        """Test de la structure complète des findings"""
        finding = {
            "id": "VULN-001",
            "title": "Test Vulnerability",
            "severity": "high",
            "cvss_score": 7.5,
            "cve_ids": ["CVE-2024-1234"],
            "finding_type": "Configuration Error",
            "description": "Detailed description",
            "remediation": "Detailed remediation",
            "business_impact": "Business impact",
            "source_data": {
                "tool": "nmap",
                "raw_output": "Raw output"
            },
            "affected_assets": ["server1"],
            "evidence": "Evidence",
            "confidence_score": 0.85,
            "exploitation_complexity": "medium",
            "status": "open"
        }
        
        # Verify all expected fields are present
        expected_fields = [
            "id", "title", "severity", "cvss_score", "finding_type",
            "description", "remediation", "business_impact", "affected_assets",
            "evidence", "confidence_score", "exploitation_complexity", "status"
        ]
        
        for field in expected_fields:
            self.assertIn(field, finding, f"Missing field: {field}")
    
    def test_summary_structure(self):
        """Test de la structure du summary"""
        summary = {
            "total_findings": 10,
            "critical": 2,
            "high": 3,
            "medium": 4,
            "low": 1,
            "info": 0
        }
        
        # Verify counts are consistent
        total = sum([summary[k] for k in ['critical', 'high', 'medium', 'low', 'info']])
        self.assertEqual(total, summary['total_findings'])


if __name__ == '__main__':
    unittest.main()
