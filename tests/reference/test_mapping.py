"""Tests for reference mapping query layer."""

from src.reference.mapping import ReferenceMapping


class TestReferenceMapping:
    def setup_method(self):
        self.rm = ReferenceMapping()

    def test_get_python_class(self):
        result = self.rm.get_python_class("MonoBehaviour")
        assert result is not None
        assert result["python_class"] == "MonoBehaviour"
        assert result["python_module"] == "src.engine.core"

    def test_get_python_class_not_found(self):
        assert self.rm.get_python_class("NonExistentClass") is None

    def test_get_all_classes(self):
        classes = self.rm.get_all_classes()
        assert len(classes) >= 10
        names = [c["unity_class"] for c in classes]
        assert "MonoBehaviour" in names
        assert "GameObject" in names
        assert "Transform" in names

    def test_get_python_method(self):
        result = self.rm.get_python_method("Component", "GetComponent")
        assert result is not None
        assert result["python_method"] == "get_component"

    def test_get_methods_for_class(self):
        methods = self.rm.get_methods_for_class("GameObject")
        assert len(methods) >= 3
        method_names = [m["unity_method"] for m in methods]
        assert "Find" in method_names

    def test_get_python_property(self):
        result = self.rm.get_python_property("Transform", "position")
        assert result is not None
        assert result["python_property"] == "position"

    def test_get_properties_for_class(self):
        props = self.rm.get_properties_for_class("Rigidbody2D")
        assert len(props) >= 4
        prop_names = [p["unity_property"] for p in props]
        assert "velocity" in prop_names

    def test_get_lifecycle_mapping(self):
        result = self.rm.get_lifecycle_mapping("Update")
        assert result is not None
        assert result["python_method"] == "update"

    def test_get_lifecycle_order(self):
        order = self.rm.get_lifecycle_order()
        assert order[0] == "Awake"
        assert "Update" in order
        assert order.index("FixedUpdate") < order.index("Update")
        assert order.index("Update") < order.index("LateUpdate")

    def test_get_enum_mapping(self):
        result = self.rm.get_enum_mapping("ForceMode2D")
        assert result is not None
        assert result["values"]["Force"] == "FORCE"
        assert result["values"]["Impulse"] == "IMPULSE"

    def test_get_pattern(self):
        result = self.rm.get_pattern("getcomponent")
        assert result is not None
        assert "get_component" in result["python_pattern"]

    def test_get_patterns_by_category(self):
        physics = self.rm.get_patterns_by_category("physics")
        assert len(physics) >= 1

    def test_get_all_patterns(self):
        patterns = self.rm.get_all_patterns()
        assert len(patterns) >= 5

    def test_get_note(self):
        result = self.rm.get_note("Naming Conventions")
        assert result is not None
        assert "PascalCase" in result["description"]

    def test_search_class(self):
        results = self.rm.search("Transform")
        assert len(results) >= 1
        types = [r["type"] for r in results]
        assert "class" in types

    def test_search_method(self):
        results = self.rm.search("GetComponent")
        assert len(results) >= 1

    def test_search_pattern(self):
        results = self.rm.search("coroutine")
        assert len(results) >= 1

    def test_completeness_report(self):
        report = self.rm.completeness_report()
        assert report["total_classes"] >= 10
        assert report["total_methods"] >= 10
        assert report["total_properties"] >= 20
        assert report["total_patterns"] >= 5
        assert report["coverage_pct"] > 0
