"""Tests for type mapper and naming conventions."""

from src.translator.type_mapper import (
    TypeMapper, pascal_to_snake, snake_to_pascal, snake_to_camel,
    camel_to_snake, convert_float_literal,
)


class TestTypeMapperCSharpToPython:
    def setup_method(self):
        self.tm = TypeMapper()

    def test_primitives(self):
        assert self.tm.csharp_to_python("int") == "int"
        assert self.tm.csharp_to_python("float") == "float"
        assert self.tm.csharp_to_python("bool") == "bool"
        assert self.tm.csharp_to_python("string") == "str"
        assert self.tm.csharp_to_python("void") == "None"

    def test_unity_types(self):
        assert self.tm.csharp_to_python("Vector2") == "Vector2"
        assert self.tm.csharp_to_python("GameObject") == "GameObject"
        assert self.tm.csharp_to_python("Rigidbody2D") == "Rigidbody2D"
        assert self.tm.csharp_to_python("Collision2D") == "Collision2D"

    def test_nullable(self):
        assert self.tm.csharp_to_python("int?") == "int | None"
        assert self.tm.csharp_to_python("float?") == "float | None"

    def test_array(self):
        assert self.tm.csharp_to_python("float[]") == "list[float]"
        assert self.tm.csharp_to_python("GameObject[]") == "list[GameObject]"

    def test_generic_list(self):
        assert self.tm.csharp_to_python("List<int>") == "list[int]"

    def test_generic_dictionary(self):
        assert self.tm.csharp_to_python("Dictionary<string, int>") == "dict[str, int]"

    def test_unknown_preserved(self):
        assert self.tm.csharp_to_python("MyCustomClass") == "MyCustomClass"


class TestTypeMapperPythonToCSharp:
    def setup_method(self):
        self.tm = TypeMapper()

    def test_primitives(self):
        assert self.tm.python_to_csharp("int") == "int"
        assert self.tm.python_to_csharp("float") == "float"
        assert self.tm.python_to_csharp("str") == "string"
        assert self.tm.python_to_csharp("None") == "void"

    def test_optional(self):
        assert self.tm.python_to_csharp("int | None") == "int?"

    def test_list(self):
        assert self.tm.python_to_csharp("list[float]") == "float[]"

    def test_dict(self):
        assert self.tm.python_to_csharp("dict[str, int]") == "Dictionary<string, int>"


class TestNamingConventions:
    def test_pascal_to_snake(self):
        assert pascal_to_snake("Update") == "update"
        assert pascal_to_snake("FixedUpdate") == "fixed_update"
        assert pascal_to_snake("OnCollisionEnter2D") == "on_collision_enter_2_d"

    def test_pascal_to_snake_camel(self):
        assert pascal_to_snake("deltaTime") == "delta_time"
        assert pascal_to_snake("inputAxis") == "input_axis"
        assert pascal_to_snake("speed") == "speed"

    def test_snake_to_pascal(self):
        assert snake_to_pascal("update") == "Update"
        assert snake_to_pascal("fixed_update") == "FixedUpdate"
        assert snake_to_pascal("on_destroy") == "OnDestroy"

    def test_snake_to_camel(self):
        assert snake_to_camel("delta_time") == "deltaTime"
        assert snake_to_camel("input_axis") == "inputAxis"
        assert snake_to_camel("speed") == "speed"

    def test_camel_to_snake(self):
        assert camel_to_snake("boundY") == "bound_y"
        assert camel_to_snake("resetDelay") == "reset_delay"


class TestFloatLiteralConversion:
    def test_with_f_suffix(self):
        assert convert_float_literal("5f") == "5.0"
        assert convert_float_literal("0.5f") == "0.5"
        assert convert_float_literal("10F") == "10.0"

    def test_without_suffix(self):
        assert convert_float_literal("5") == "5"
        assert convert_float_literal("0.5") == "0.5"

    def test_decimal(self):
        assert convert_float_literal("1.0f") == "1.0"
