"""Tests that all engine classes have corresponding reference mappings."""

from src.reference.mapping import ReferenceMapping


class TestMappingCompleteness:
    def setup_method(self):
        self.rm = ReferenceMapping()

    def test_all_engine_classes_mapped(self):
        """Every major engine class should have a mapping entry."""
        required = [
            "MonoBehaviour", "GameObject", "Transform",
            "Rigidbody2D", "BoxCollider2D", "CircleCollider2D",
            "Camera", "SpriteRenderer",
            "Vector2", "Vector3", "Quaternion", "Mathf",
        ]
        for cls_name in required:
            result = self.rm.get_python_class(cls_name)
            assert result is not None, f"Missing mapping for {cls_name}"

    def test_all_lifecycle_methods_mapped(self):
        """Every lifecycle method used by MonoBehaviour should have a mapping."""
        required = [
            "Awake", "Start", "Update", "FixedUpdate", "LateUpdate",
            "OnDestroy", "OnEnable", "OnDisable",
            "OnCollisionEnter2D", "OnCollisionExit2D",
            "OnTriggerEnter2D", "OnTriggerExit2D",
        ]
        for method in required:
            result = self.rm.get_lifecycle_mapping(method)
            assert result is not None, f"Missing lifecycle mapping for {method}"

    def test_key_methods_mapped(self):
        """Key methods used in game scripts should have mappings."""
        required_methods = [
            ("Component", "GetComponent"),
            ("GameObject", "Find"),
            ("GameObject", "FindWithTag"),
            ("GameObject", "AddComponent"),
            ("Object", "Destroy"),
            ("Transform", "Translate"),
            ("Input", "GetAxis"),
            ("Input", "GetKey"),
            ("Rigidbody2D", "AddForce"),
        ]
        for cls, method in required_methods:
            result = self.rm.get_python_method(cls, method)
            assert result is not None, f"Missing method mapping for {cls}.{method}"

    def test_key_properties_mapped(self):
        """Key properties should have mappings."""
        required_props = [
            ("Transform", "position"),
            ("Transform", "rotation"),
            ("Rigidbody2D", "velocity"),
            ("Time", "deltaTime"),
            ("GameObject", "name"),
            ("GameObject", "tag"),
            ("Component", "enabled"),
        ]
        for cls, prop in required_props:
            result = self.rm.get_python_property(cls, prop)
            assert result is not None, f"Missing property mapping for {cls}.{prop}"
