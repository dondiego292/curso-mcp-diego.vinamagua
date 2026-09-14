"""Módulo de conversión de temperatura siguiendo Spec-Driven Development (SDD).

Soporta conversiones entre Celsius, Fahrenheit y Kelvin con validación
rigurosa de tipos, límites físicos (cero absoluto en Kelvin) y redondeo a 2 decimales.
"""

from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import math
import sys
from typing import Any, Union


class UnidadTemperatura(str, Enum):
    """Unidades de temperatura soportadas."""
    CELSIUS = "C"
    FAHRENHEIT = "F"
    KELVIN = "K"


# Mapeo de alias para mayor flexibilidad en entradas de usuario
_ALIAS_UNIDADES = {
    "c": UnidadTemperatura.CELSIUS,
    "celsius": UnidadTemperatura.CELSIUS,
    "°c": UnidadTemperatura.CELSIUS,
    "f": UnidadTemperatura.FAHRENHEIT,
    "fahrenheit": UnidadTemperatura.FAHRENHEIT,
    "°f": UnidadTemperatura.FAHRENHEIT,
    "k": UnidadTemperatura.KELVIN,
    "kelvin": UnidadTemperatura.KELVIN,
    "°k": UnidadTemperatura.KELVIN,
}


def normalizar_unidad(unidad: Any) -> UnidadTemperatura:
    """Valida y normaliza una unidad de temperatura a UnidadTemperatura.

    Args:
        unidad: Cadena que representa la unidad (ej. 'C', 'celsius', 'F', 'K').

    Returns:
        UnidadTemperatura normalizada.

    Raises:
        ValueError: Si la unidad está vacía o no es soportada.
    """
    if unidad is None:
        raise ValueError("La unidad no puede estar vacía.")

    if not isinstance(unidad, str):
        raise ValueError(f"La unidad debe ser una cadena de texto, se recibió: {type(unidad).__name__}.")

    u_limpia = unidad.strip().lower()
    if not u_limpia:
        raise ValueError("La unidad no puede estar vacía.")

    if u_limpia in _ALIAS_UNIDADES:
        return _ALIAS_UNIDADES[u_limpia]

    raise ValueError(
        f"Unidad no soportada: '{unidad}'. Las unidades válidas son Celsius (C), Fahrenheit (F) y Kelvin (K)."
    )


def _validar_y_convertir_a_float(valor: Any) -> float:
    """Valida que el valor no esté vacío y sea numérico, retornándolo como float.

    Args:
        valor: Valor numérico o cadena de texto que represente un número.

    Returns:
        float: Valor numérico parseado.

    Raises:
        ValueError: Si la entrada está vacía, no es numérica, o es NaN/infinito.
    """
    if valor is None:
        raise ValueError("La entrada no puede estar vacía.")

    # En Python bool es subclase de int (True == 1, False == 0), debemos rechazarlo explícitamente
    if isinstance(valor, bool):
        raise ValueError(
            f"Entrada no numérica: {valor}. La temperatura debe ser un valor numérico válido."
        )

    if isinstance(valor, str):
        cadena_limpia = valor.strip()
        if not cadena_limpia:
            raise ValueError("La entrada no puede estar vacía.")
        try:
            num = float(cadena_limpia)
        except ValueError:
            raise ValueError(
                f"Entrada no numérica: '{valor}'. La temperatura debe ser un valor numérico válido."
            )
    elif isinstance(valor, (int, float)):
        num = float(valor)
    else:
        raise ValueError(
            f"Entrada no numérica: '{valor}'. La temperatura debe ser un valor numérico válido."
        )

    if math.isnan(num) or math.isinf(num):
        raise ValueError(f"La temperatura no puede ser NaN ni infinito: '{valor}'.")

    return num


def redondear_2_decimales(valor: float) -> float:
    """Redondea un número a 2 decimales según el estándar aritmético formal (ROUND_HALF_UP)."""
    return float(Decimal(f"{valor:.10f}").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def convertir_temperatura(
    valor: Any,
    unidad_origen: Union[str, UnidadTemperatura],
    unidad_destino: Union[str, UnidadTemperatura],
) -> float:
    """Convierte una temperatura entre Celsius, Fahrenheit y Kelvin.

    Criterios de aceptación:
    - Convierte correctamente de Celsius a Fahrenheit y viceversa.
    - Convierte correctamente de Celsius a Kelvin y viceversa.
    - Convierte correctamente de Fahrenheit a Kelvin y viceversa.
    - Redondea el resultado a 2 decimales.
    - Rechaza temperaturas Kelvin inferiores a 0.

    Casos borde:
    - Entrada vacía -> muestra mensaje de error claro.
    - Entrada no numérica -> muestra mensaje de error claro.
    - Temperatura Kelvin inferior a 0 -> rechaza la conversión.
    - Conversión de una unidad a la misma unidad -> devuelve el mismo valor redondeado a 2 decimales.

    Args:
        valor: Temperatura a convertir (int, float o str convertible a número).
        unidad_origen: Unidad de origen ('C', 'F', 'K' o nombres completos).
        unidad_destino: Unidad de destino ('C', 'F', 'K' o nombres completos).

    Returns:
        float: Temperatura convertida redondeada a 2 decimales.

    Raises:
        ValueError: Si las entradas no cumplen los criterios de aceptación o casos borde.
    """
    temp = _validar_y_convertir_a_float(valor)
    origen = normalizar_unidad(unidad_origen)
    destino = normalizar_unidad(unidad_destino)

    # Criterio y Caso borde: Rechaza temperaturas Kelvin inferiores a 0 en origen
    if origen == UnidadTemperatura.KELVIN and temp < 0:
        raise ValueError(
            f"Temperatura Kelvin inferior a 0 ({temp} K): la escala Kelvin no admite valores negativos (el cero absoluto es 0 K)."
        )

    # Caso borde: Misma unidad de origen y destino
    if origen == destino:
        return redondear_2_decimales(temp)

    resultado: float

    # Conversión desde Celsius
    if origen == UnidadTemperatura.CELSIUS:
        if destino == UnidadTemperatura.FAHRENHEIT:
            resultado = (temp * 9.0 / 5.0) + 32.0
        elif destino == UnidadTemperatura.KELVIN:
            resultado = temp + 273.15

    # Conversión desde Fahrenheit
    elif origen == UnidadTemperatura.FAHRENHEIT:
        if destino == UnidadTemperatura.CELSIUS:
            resultado = (temp - 32.0) * 5.0 / 9.0
        elif destino == UnidadTemperatura.KELVIN:
            resultado = ((temp - 32.0) * 5.0 / 9.0) + 273.15

    # Conversión desde Kelvin
    elif origen == UnidadTemperatura.KELVIN:
        if destino == UnidadTemperatura.CELSIUS:
            resultado = temp - 273.15
        elif destino == UnidadTemperatura.FAHRENHEIT:
            resultado = ((temp - 273.15) * 9.0 / 5.0) + 32.0

    # Criterio y Caso borde: Rechaza temperaturas Kelvin inferiores a 0 en destino
    if destino == UnidadTemperatura.KELVIN and resultado < 0:
        raise ValueError(
            f"Temperatura Kelvin inferior a 0: la conversión resulta en {resultado:.2f} K, lo cual es inferior al cero absoluto (0 K)."
        )

    return redondear_2_decimales(resultado)


# Alias en inglés para interoperabilidad
convert_temperature = convertir_temperatura


# Funciones específicas directas
def celsius_a_fahrenheit(celsius: Any) -> float:
    """Convierte de Celsius a Fahrenheit redondeado a 2 decimales."""
    return convertir_temperatura(celsius, UnidadTemperatura.CELSIUS, UnidadTemperatura.FAHRENHEIT)


def fahrenheit_a_celsius(fahrenheit: Any) -> float:
    """Convierte de Fahrenheit a Celsius redondeado a 2 decimales."""
    return convertir_temperatura(fahrenheit, UnidadTemperatura.FAHRENHEIT, UnidadTemperatura.CELSIUS)


def celsius_a_kelvin(celsius: Any) -> float:
    """Convierte de Celsius a Kelvin redondeado a 2 decimales."""
    return convertir_temperatura(celsius, UnidadTemperatura.CELSIUS, UnidadTemperatura.KELVIN)


def kelvin_a_celsius(kelvin: Any) -> float:
    """Convierte de Kelvin a Celsius redondeado a 2 decimales."""
    return convertir_temperatura(kelvin, UnidadTemperatura.KELVIN, UnidadTemperatura.CELSIUS)


def fahrenheit_a_kelvin(fahrenheit: Any) -> float:
    """Convierte de Fahrenheit a Kelvin redondeado a 2 decimales."""
    return convertir_temperatura(fahrenheit, UnidadTemperatura.FAHRENHEIT, UnidadTemperatura.KELVIN)


def kelvin_a_fahrenheit(kelvin: Any) -> float:
    """Convierte de Kelvin a Fahrenheit redondeado a 2 decimales."""
    return convertir_temperatura(kelvin, UnidadTemperatura.KELVIN, UnidadTemperatura.FAHRENHEIT)


# Alias en inglés para las funciones directas
celsius_to_fahrenheit = celsius_a_fahrenheit
fahrenheit_to_celsius = fahrenheit_a_celsius
celsius_to_kelvin = celsius_a_kelvin
kelvin_to_celsius = kelvin_a_celsius
fahrenheit_to_kelvin = fahrenheit_a_kelvin
kelvin_to_fahrenheit = kelvin_a_fahrenheit


class ConversorTemperatura:
    """Clase envoltorio para el conversor de temperatura."""

    @staticmethod
    def convertir(
        valor: Any,
        unidad_origen: Union[str, UnidadTemperatura],
        unidad_destino: Union[str, UnidadTemperatura],
    ) -> float:
        """Convierte una temperatura entre unidades."""
        return convertir_temperatura(valor, unidad_origen, unidad_destino)

    @staticmethod
    def convert(
        valor: Any,
        unidad_origen: Union[str, UnidadTemperatura],
        unidad_destino: Union[str, UnidadTemperatura],
    ) -> float:
        """Alias en inglés para convertir."""
        return convertir_temperatura(valor, unidad_origen, unidad_destino)


# Alias en inglés de la clase
TemperatureConverter = ConversorTemperatura


def cli_interactiva() -> None:
    """Interfaz CLI interactiva enriquecida con soporte para Rich."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.prompt import Prompt

        console = Console()
        console.print(
            Panel.fit(
                "[bold cyan]🌡️  Conversor de Temperatura (Spec-Driven Development)[/bold cyan]\n"
                "[dim]Convierte entre Celsius, Fahrenheit y Kelvin cumpliendo la especificación técnica.[/dim]",
                border_style="cyan",
            )
        )

        while True:
            console.print("\n[bold yellow]Opciones disponibles:[/bold yellow]")
            console.print("  [bold]1[/bold] - Realizar una conversión de temperatura")
            console.print("  [bold]2[/bold] - Ver tabla comparativa de puntos clave")
            console.print("  [bold]q[/bold] - Salir")

            opcion = Prompt.ask("Selecciona una opción", choices=["1", "2", "q"], default="1")
            if opcion == "q":
                console.print("[dim]¡Hasta luego![/dim]")
                break

            if opcion == "1":
                val_input = Prompt.ask("Ingresa el valor de temperatura")
                origen_input = Prompt.ask(
                    "Unidad de origen", choices=["C", "F", "K", "celsius", "fahrenheit", "kelvin"], default="C"
                )
                destino_input = Prompt.ask(
                    "Unidad de destino", choices=["C", "F", "K", "celsius", "fahrenheit", "kelvin"], default="F"
                )

                try:
                    res = convertir_temperatura(val_input, origen_input, destino_input)
                    origen_norm = normalizar_unidad(origen_input).value
                    destino_norm = normalizar_unidad(destino_input).value

                    res_table = Table.grid(padding=(0, 2))
                    res_table.add_column("Key", style="cyan bold")
                    res_table.add_column("Value")
                    res_table.add_row("Entrada:", f"{val_input} °{origen_norm}" if origen_norm != "K" else f"{val_input} K")
                    res_table.add_row("Resultado:", f"[bold green]{res:.2f} °{destino_norm}[/bold green]" if destino_norm != "K" else f"[bold green]{res:.2f} K[/bold green]")
                    console.print(Panel(res_table, title="[bold green]Conversión Exitosa[/bold green]", border_style="green"))
                except ValueError as err:
                    console.print(Panel(f"[bold red]Error:[/bold red] {err}", title="[bold red]Error de Validación[/bold red]", border_style="red"))

            elif opcion == "2":
                table = Table(title="Puntos de Referencia de Temperatura", header_style="bold magenta")
                table.add_column("Punto Físico", style="bold")
                table.add_column("Celsius (°C)", justify="right")
                table.add_column("Fahrenheit (°F)", justify="right")
                table.add_column("Kelvin (K)", justify="right")

                puntos = [
                    ("Cero Absoluto", -273.15, -459.67, 0.0),
                    ("Congelación del Agua", 0.0, 32.0, 273.15),
                    ("Temperatura Corporal Media", 37.0, 98.6, 310.15),
                    ("Ebullición del Agua", 100.0, 212.0, 373.15),
                ]
                for nombre, c, f, k in puntos:
                    table.add_row(nombre, f"{c:.2f}", f"{f:.2f}", f"{k:.2f}")

                console.print(table)

    except ImportError:
        # Fallback sin Rich si no está instalado
        print("\n=== Conversor de Temperatura ===")
        val_input = input("Ingresa la temperatura: ")
        origen_input = input("Unidad de origen (C/F/K): ")
        destino_input = input("Unidad de destino (C/F/K): ")
        try:
            res = convertir_temperatura(val_input, origen_input, destino_input)
            print(f"Resultado: {res:.2f}")
        except ValueError as err:
            print(f"Error: {err}")


def main() -> None:
    """Punto de entrada principal para línea de comandos."""
    if len(sys.argv) == 4:
        # Formato: python conversor_temperatura.py <valor> <origen> <destino>
        val, origen, destino = sys.argv[1], sys.argv[2], sys.argv[3]
        try:
            res = convertir_temperatura(val, origen, destino)
            print(f"{res:.2f}")
        except ValueError as err:
            print(f"Error: {err}", file=sys.stderr)
            sys.exit(1)
    else:
        cli_interactiva()


if __name__ == "__main__":
    main()
