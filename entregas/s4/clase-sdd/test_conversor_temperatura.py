"""Suite completa de pruebas unitarias para el Conversor de Temperatura.

Valida rigurosamente la especificación bajo Spec-Driven Development (SDD):
- Criterios de aceptación (Celsius <-> Fahrenheit, Celsius <-> Kelvin, Fahrenheit <-> Kelvin,
  redondeo a 2 decimales, rechazo de Kelvin < 0).
- Casos borde (entrada vacía, entrada no numérica, Kelvin < 0, misma unidad).
- Robustez adicional (alias de unidades, mayúsculas/minúsculas, tipos string numéricos, API OO y funcional).
"""

import unittest
from conversor_temperatura import (
    convertir_temperatura,
    convert_temperature,
    celsius_a_fahrenheit,
    fahrenheit_a_celsius,
    celsius_a_kelvin,
    kelvin_a_celsius,
    fahrenheit_a_kelvin,
    kelvin_a_fahrenheit,
    ConversorTemperatura,
    TemperatureConverter,
    UnidadTemperatura,
)


class TestConversorTemperaturaCriteriosAceptacion(unittest.TestCase):
    """Pruebas de los Criterios de Aceptación especificados."""

    def test_celsius_a_fahrenheit_y_viceversa(self):
        """Convierte correctamente de Celsius a Fahrenheit y viceversa."""
        casos = [
            (0, 32.00),         # Punto de congelación del agua
            (100, 212.00),      # Punto de ebullición del agua
            (-40, -40.00),      # Punto de cruce C y F
            (37, 98.60),        # Temperatura corporal
            (25, 77.00),        # Temperatura ambiente típica
            (-10, 14.00),
        ]
        for c, f in casos:
            with self.subTest(celsius=c, fahrenheit=f):
                # Celsius -> Fahrenheit
                res_f = convertir_temperatura(c, "C", "F")
                self.assertAlmostEqual(res_f, f, places=2)
                # Fahrenheit -> Celsius
                res_c = convertir_temperatura(f, "F", "C")
                self.assertAlmostEqual(res_c, c, places=2)

    def test_celsius_a_kelvin_y_viceversa(self):
        """Convierte correctamente de Celsius a Kelvin y viceversa."""
        casos = [
            (0, 273.15),
            (100, 373.15),
            (-273.15, 0.00),   # Cero absoluto
            (25, 298.15),
            (-40, 233.15),
        ]
        for c, k in casos:
            with self.subTest(celsius=c, kelvin=k):
                # Celsius -> Kelvin
                res_k = convertir_temperatura(c, "C", "K")
                self.assertAlmostEqual(res_k, k, places=2)
                # Kelvin -> Celsius
                res_c = convertir_temperatura(k, "K", "C")
                self.assertAlmostEqual(res_c, c, places=2)

    def test_fahrenheit_a_kelvin_y_viceversa(self):
        """Convierte correctamente de Fahrenheit a Kelvin y viceversa."""
        casos = [
            (32.00, 273.15),
            (212.00, 373.15),
            (-459.67, 0.00),   # Cero absoluto
            (98.60, 310.15),
        ]
        for f, k in casos:
            with self.subTest(fahrenheit=f, kelvin=k):
                # Fahrenheit -> Kelvin
                res_k = convertir_temperatura(f, "F", "K")
                self.assertAlmostEqual(res_k, k, places=2)
                # Kelvin -> Fahrenheit
                res_f = convertir_temperatura(k, "K", "F")
                self.assertAlmostEqual(res_f, f, places=2)

    def test_redondeo_a_dos_decimales(self):
        """Redondea el resultado a 2 decimales."""
        # 100 Fahrenheit a Celsius: (100 - 32) * 5 / 9 = 37.777777... -> 37.78
        res1 = convertir_temperatura(100, "F", "C")
        self.assertEqual(res1, 37.78)

        # 0 Fahrenheit a Kelvin: (0 - 32) * 5 / 9 + 273.15 = 255.372222... -> 255.37
        res2 = convertir_temperatura(0, "F", "K")
        self.assertEqual(res2, 255.37)

        # 80 Fahrenheit a Celsius: (80 - 32) * 5 / 9 = 26.666666... -> 26.67
        res3 = convertir_temperatura(80, "F", "C")
        self.assertEqual(res3, 26.67)

        # 300 Kelvin a Fahrenheit: (300 - 273.15) * 9 / 5 + 32 = 80.33
        res4 = convertir_temperatura(300, "K", "F")
        self.assertEqual(res4, 80.33)

    def test_rechaza_temperaturas_kelvin_inferiores_a_cero(self):
        """Rechaza temperaturas Kelvin inferiores a 0."""
        temperaturas_kelvin_invalidas = [-0.01, -1, -5, -273.15, -1000]

        for k in temperaturas_kelvin_invalidas:
            with self.subTest(kelvin=k):
                # Conversión de Kelvin a Celsius
                with self.assertRaises(ValueError) as ctx:
                    convertir_temperatura(k, "K", "C")
                self.assertTrue(
                    "kelvin" in str(ctx.exception).lower() and "0" in str(ctx.exception)
                )

                # Conversión de Kelvin a Fahrenheit
                with self.assertRaises(ValueError) as ctx:
                    convertir_temperatura(k, "K", "F")
                self.assertTrue(
                    "kelvin" in str(ctx.exception).lower() and "0" in str(ctx.exception)
                )

                # Conversión de Kelvin a Kelvin (misma unidad negativa)
                with self.assertRaises(ValueError) as ctx:
                    convertir_temperatura(k, "K", "K")
                self.assertTrue(
                    "kelvin" in str(ctx.exception).lower() and "0" in str(ctx.exception)
                )

        # Conversión hacia Kelvin que resulte en negativo (< 0 K)
        with self.assertRaises(ValueError) as ctx:
            convertir_temperatura(-300, "C", "K")  # -300 C = -26.85 K
        self.assertTrue(
            "kelvin" in str(ctx.exception).lower() and "0" in str(ctx.exception)
        )


class TestConversorTemperaturaCasosBorde(unittest.TestCase):
    """Pruebas de los Casos Borde especificados."""

    def test_caso_borde_entrada_vacia(self):
        """Entrada vacía -> debe mostrar un mensaje de error claro."""
        entradas_vacias = ["", "   ", "\t", "\n", None]

        for entrada in entradas_vacias:
            with self.subTest(entrada=entrada):
                with self.assertRaises(ValueError) as ctx:
                    convertir_temperatura(entrada, "C", "F")
                mensaje = str(ctx.exception).lower()
                self.assertTrue(
                    "vacía" in mensaje or "vacia" in mensaje,
                    f"El mensaje de error '{ctx.exception}' no indica que está vacía.",
                )

    def test_caso_borde_entrada_no_numerica(self):
        """Entrada no numérica, por ejemplo 'abc' -> debe mostrar un mensaje de error claro."""
        entradas_no_numericas = [
            "abc",
            "12a",
            "temperatura",
            "12.34.56",
            "--5",
            True,       # En Python bool hereda de int, debe rechazarse explícitamente
            False,
            [],
            {},
        ]

        for entrada in entradas_no_numericas:
            with self.subTest(entrada=entrada):
                with self.assertRaises(ValueError) as ctx:
                    convertir_temperatura(entrada, "C", "F")
                mensaje = str(ctx.exception).lower()
                self.assertTrue(
                    "no numér" in mensaje or "no numer" in mensaje or "numérico" in mensaje,
                    f"El mensaje de error '{ctx.exception}' no es claro sobre el error no numérico.",
                )

    def test_caso_borde_temperatura_kelvin_inferior_a_cero(self):
        """Temperatura Kelvin inferior a 0 -> debe rechazar la conversión."""
        with self.assertRaises(ValueError) as ctx:
            convertir_temperatura(-1, "K", "C")
        self.assertIn("kelvin", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            convertir_temperatura(-10.5, "K", "F")
        self.assertIn("kelvin", str(ctx.exception).lower())

        # Exactamente 0 K debe ser aceptado
        self.assertEqual(convertir_temperatura(0, "K", "C"), -273.15)
        self.assertEqual(convertir_temperatura(0, "K", "K"), 0.0)

    def test_caso_borde_misma_unidad(self):
        """Conversión de una unidad a la misma unidad -> debe devolver el mismo valor."""
        # Celsius a Celsius
        self.assertEqual(convertir_temperatura(25, "C", "C"), 25.00)
        self.assertEqual(convertir_temperatura(0, "celsius", "celsius"), 0.00)
        self.assertEqual(convertir_temperatura(-15.5, "C", "C"), -15.50)

        # Fahrenheit a Fahrenheit
        self.assertEqual(convertir_temperatura(32, "F", "F"), 32.00)
        self.assertEqual(convertir_temperatura(-40, "fahrenheit", "fahrenheit"), -40.00)

        # Kelvin a Kelvin (valores >= 0)
        self.assertEqual(convertir_temperatura(0, "K", "K"), 0.00)
        self.assertEqual(convertir_temperatura(300, "kelvin", "kelvin"), 300.00)

        # Misma unidad con redondeo a 2 decimales si tiene más decimales
        self.assertEqual(convertir_temperatura(25.555, "C", "C"), 25.56)


class TestConversorTemperaturaRobustezYFlexibilidad(unittest.TestCase):
    """Pruebas de robustez adicionales (alias, cadenas numéricas, API OO y funcional)."""

    def test_entradas_numericas_como_string(self):
        """Acepta strings con valores numéricos válidos (incluyendo espacios)."""
        self.assertEqual(convertir_temperatura(" 100 ", "C", "F"), 212.00)
        self.assertEqual(convertir_temperatura("-40.0", "C", "F"), -40.00)
        self.assertEqual(convertir_temperatura("0", "K", "C"), -273.15)

    def test_flexibilidad_unidades(self):
        """Acepta nombres en minúsculas, mayúsculas, nombres completos y símbolos de grado."""
        self.assertEqual(convertir_temperatura(100, "celsius", "fahrenheit"), 212.00)
        self.assertEqual(convertir_temperatura(100, "CELSIUS", "FAHRENHEIT"), 212.00)
        self.assertEqual(convertir_temperatura(100, "°c", "°f"), 212.00)
        self.assertEqual(convertir_temperatura(0, "°C", "k"), 273.15)
        self.assertEqual(convertir_temperatura(273.15, "kelvin", "°c"), 0.00)

    def test_unidades_invalidas(self):
        """Rechaza unidades desconocidas o vacías."""
        with self.assertRaises(ValueError):
            convertir_temperatura(100, "Rankine", "C")

        with self.assertRaises(ValueError):
            convertir_temperatura(100, "C", "")

        with self.assertRaises(ValueError):
            convertir_temperatura(100, "", "F")

        with self.assertRaises(ValueError):
            convertir_temperatura(100, None, "F")

    def test_funciones_directas_y_aliases(self):
        """Verifica las funciones directas y aliases en inglés."""
        self.assertEqual(celsius_a_fahrenheit(0), 32.00)
        self.assertEqual(fahrenheit_a_celsius(32), 0.00)
        self.assertEqual(celsius_a_kelvin(0), 273.15)
        self.assertEqual(kelvin_a_celsius(273.15), 0.00)
        self.assertEqual(fahrenheit_a_kelvin(32), 273.15)
        self.assertEqual(kelvin_a_fahrenheit(273.15), 32.00)

        # Alias en inglés
        self.assertEqual(convert_temperature(0, "C", "F"), 32.00)

    def test_clase_conversor(self):
        """Verifica los métodos estáticos de la clase ConversorTemperatura."""
        self.assertEqual(ConversorTemperatura.convertir(100, "C", "F"), 212.00)
        self.assertEqual(TemperatureConverter.convert(212, "F", "C"), 100.00)


if __name__ == "__main__":
    unittest.main()
