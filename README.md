```markdown
## Environment check — Class 1



Haz un último commit y push:

```bash
git add .
git commit -m "Class 1: environment check"
git push
```

**Cierre de la sesión:** esta práctica no se entrega ni se sube a ninguna plataforma. Al
terminar, muéstrale a tu docente (o dile en voz alta en la sesión) que tu tabla de
`verify_environment.py` salió en verde. El objetivo de hoy es que tu entorno quede listo —
no generar un entregable.

## Clase 2 — APIs de IA Generativa y memoria conversacional

### Conversación de 8 turnos (Paso 7)

Ver evidencia en `entregas/s02/evidencia/memoria.png`.

<pega aquí también el texto de la salida, aunque ya esté en la captura>

### Por qué elegí ventana deslizante

<explica en 2-3 líneas por qué esta estrategia y no resumen progresivo,
memoria selectiva o almacenamiento externo, para este caso>

### Límite de solicitudes provocado (Paso 9)

Ver evidencia en `entregas/s02/evidencia/rate_limit.png`.

<una línea confirmando que el error se manejó sin que el programa se cayera>


**Nota sobre el modelo:** usé `gemini-3.5-flash-lite` en lugar de `gemini-2.5-flash`, porque mi proyecto de Google Cloud no tenía acceso habilitado a `gemini-2.5-flash` (la clave fallaba solo con ese modelo, no con los más recientes).

### Por qué elegí ventana deslizante

Elegí ventana deslizante porque es la estrategia más simple y barata: no agrega llamadas extra al modelo (como sí lo haría un resumen progresivo) ni requiere lógica de selección de qué guardar (memoria selectiva) ni infraestructura adicional (almacenamiento externo). Para una conversación corta como la de esta práctica (8 turnos, `MAX_TURNS=10`), el trade-off de perder el inicio de la charla cuando crece demasiado no aplica todavía — pero lo comprobé aparte con `demo_forgetting()` usando `MAX_TURNS=3`.

### Límite de solicitudes provocado (Paso 9)

Ver evidencia en `entregas/s02/evidencia/rate_limit.png`.

El código implementa el manejo de `ClientError` (429, con reintento y backoff exponencial) y `ServerError` (5xx, mismo tratamiento) tal como pide la práctica. Sin embargo, no logré reproducir el error 429 en la práctica: mi cuenta de Google Cloud tiene facturación (billing) habilitada, lo que according a la documentación de Gemini eleva automáticamente el proyecto al "Tier 1" de uso, con un límite de solicitudes por minuto mucho más alto que el del tier gratuito (decenas o cientos de RPM en vez de ~15). Incluso subiendo `trigger_rate_limit()` a 1000 iteraciones no alcancé el límite. El manejo de errores queda implementado y listo para dispararse si el límite se alcanza, pero no pude capturar la evidencia del 429 real con este proyecto.