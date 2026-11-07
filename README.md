# Clasificación de malware con una red neuronal convolucional

Proyecto de la materia de **Minería de Datos** (Facultad de Ingeniería, UNAM, Gpo. 03, semestre 2027-1).

**Autor:** Lee Robles Leonardo Alan

---

## ¿De qué trata este proyecto?

Un programa de computadora (por ejemplo, un `.exe`) es, al final, una larga lista de bytes. Cada byte es un número entre 0 y 255. Si acomodamos esa lista en una cuadrícula y pintamos cada número como un tono de gris, el programa se convierte en una **imagen**.

Lo interesante es que los programas maliciosos de una misma familia (por ejemplo, distintas versiones de un mismo virus) suelen compartir partes de su código, así que sus imágenes se ven parecidas, con texturas y patrones similares. Entonces, en lugar de analizar el código, podemos **usar una red neuronal que reconozca esas texturas**, igual que se hace para reconocer objetos en fotografías.

En este proyecto se entrena una **red neuronal convolucional (CNN)** con PyTorch que, dada la imagen de un programa, decide a cuál de estas **26 clases** pertenece:

- 25 familias de malware (del dataset Malimg), y
- 1 clase de software **benigno** (programas que no son maliciosos).

## ¿Cómo funciona?

1. **Exploración de los datos:** se revisa cuántas imágenes hay de cada familia, su tamaño y cómo se ven.
2. **Preparación:** las imágenes se redimensionan todas a 256x256 píxeles, se dividen en entrenamiento (80%), validación (10%) y prueba (10%), y se normalizan. Como hay familias con muchas más imágenes que otras, se usan *pesos de clase* para que las familias pequeñas no se ignoren.
3. **Entrenamiento:** una CNN de tres capas convolucionales aprende durante 10 épocas.
4. **Evaluación:** se mide qué tan bien clasifica imágenes que nunca vio (validación y prueba), con gráficas, matrices de confusión y métricas por familia.

## Los datos

- **Malimg** (Nataraj et al., 2011): imágenes en escala de grises de 25 familias de malware. Es un dataset público y muy usado en investigación.
- **Clase benigna (`benign_samples`):** se generó con el mismo método del artículo de Malimg usando el script `generate_benign_samples.py`. El script recorre los archivos `.exe` y `.dll` de la carpeta `C:\Windows\System32` de un equipo con Windows y convierte cada uno en una imagen en escala de grises (el ancho depende del tamaño del archivo y los bytes que faltan se rellenan con ceros).

> Las imágenes son solo representaciones visuales: **no contienen programas ejecutables**, por lo que no hay riesgo al abrirlas.

## Resultados

Resultados con las imágenes del conjunto de **prueba** (datos que el modelo nunca vio durante el entrenamiento):

| Métrica | Resultado |
|---|---|
| Accuracy (porcentaje de aciertos) | **92.89%** |
| F1 ponderado | 0.9339 |
| F1 macro | 0.8001 |

En palabras sencillas:

- **El modelo acierta alrededor de 9 de cada 10 imágenes** y obtiene resultados casi iguales en entrenamiento (92.4%), validación (93.5%) y prueba (92.9%), lo que significa que no está "memorizando" los datos.
- **Casi ningún malware se clasifica como benigno** (precisión de 0.999 en la clase benigna). A cambio, alrededor del 8.6% de los programas benignos se marcan por error como malware (falsas alarmas).
- **Hay familias que le cuestan más:** `Autorun.K` (siempre la confunde con `Yuner.A`) y `Swizzor.gen!E` (la confunde con `Swizzor.gen!I`). Muchas de las confusiones son entre variantes de una misma familia, que se parecen mucho.
- El F1 macro (0.80) es menor que el accuracy porque cuenta igual a todas las familias, incluidas las pequeñas donde el modelo falla más.

El análisis completo, con todas las gráficas, está dentro del notebook.

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| `Practica_3_6_Redes_Neuronales_Lee_Robles.ipynb` | Notebook con todo el proyecto: exploración, preparación, entrenamiento, evaluación, resultados y conclusiones |
| `generate_benign_samples.py` | Script que genera las imágenes de la clase benigna (solo Windows) |
| `cnn_malimg.pth` | Pesos del modelo ya entrenado |
| `README.md` | Este archivo |

> El dataset (`malimg_dataset/`) y la carpeta de imágenes ya redimensionadas (`cache_256/`, de alrededor de 1.5 GB) **no están incluidos** por su tamaño. La segunda se genera sola al ejecutar el notebook.

## Cómo ejecutarlo

**1. Instala las librerías** (se necesita Python 3):

```bash
pip install torch pandas numpy scikit-learn seaborn matplotlib pillow tqdm jupyter
```

**2. Consigue los datos.** Descarga el dataset Malimg (es público y se encuentra fácilmente buscando "Malimg dataset" en internet) y colócalo en una carpeta llamada `malimg_dataset`, con una subcarpeta por cada familia (con las imágenes `.png` adentro). La clase benigna va en una subcarpeta llamada `benign_samples`. Para generarla, ejecuta `generate_benign_samples.py` en una computadora con Windows (`python generate_benign_samples.py`); crea la carpeta `benign_samples` y solo hay que moverla dentro de `malimg_dataset`.

```
malimg_dataset/
├── Adialer.C/
├── Agent.FYI/
├── ...
└── benign_samples/
```

**3. Abre el notebook** y ejecuta todas las celdas de arriba abajo:

```bash
jupyter notebook
```

Notas:

- La primera vez tarda un poco más porque redimensiona todas las imágenes una sola vez.
- El entrenamiento tarda alrededor de **37 minutos en CPU** (10 épocas). Si tienes una GPU compatible con PyTorch, la usa automáticamente.
- Al terminar el entrenamiento, el notebook guarda los pesos en `cnn_malimg.pth`.

## Usar el modelo ya entrenado

Para cargar los pesos guardados sin entrenar de nuevo (requiere la definición de la clase `CNN` del notebook):

```python
import torch

checkpoint = torch.load('cnn_malimg.pth', map_location='cpu', weights_only=True)
model = CNN(in_channels=1, num_classes=len(checkpoint['classes']))
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

print(checkpoint['classes'])  # nombres de las 26 clases, en el orden de salida de la red
```

El archivo guarda también el tamaño de imagen que espera la red (256x256) y la lista de clases.

## Limitaciones

- El modelo se entrenó solo 10 épocas y no se probaron distintos hiperparámetros.
- Los datos están muy desbalanceados: la clase benigna es alrededor del 62% del conjunto de prueba y algunas familias tienen muy pocas imágenes, por lo que sus métricas son poco estables.
- Malimg tiene muchas imágenes casi iguales dentro de cada familia, así que los resultados podrían ser más optimistas de lo que serían con malware nuevo.
- La clase benigna se generó solo con archivos `.exe` y `.dll` de `C:\Windows\System32` de un equipo, es decir, archivos del propio Windows. Puede no representar a todo el software no malicioso (por ejemplo, programas de terceros), y es posible que la red aprenda a reconocer el estilo de esos archivos y no lo que distingue a un programa benigno de uno malicioso.
- No se midió por separado el efecto del *data augmentation*.

## Referencias

- Nataraj, L., Yegneswaran, V., Porras, P., & Zhang, X. (2011). Malware images: Visualization and automatic classification. En *Proceedings of the 8th International Symposium on Visualization for Cyber Security (VizSec '11)* (pp. 1–7). ACM. https://dl.acm.org/doi/10.1145/2016904.2016908
- Kingma, D. P., & Ba, J. (2015). Adam: A method for stochastic optimization. *ICLR 2015*. https://arxiv.org/abs/1412.6980
- Paszke, A., et al. (2019). PyTorch: An imperative style, high-performance deep learning library. *NeurIPS 2019*. https://arxiv.org/abs/1912.01703
