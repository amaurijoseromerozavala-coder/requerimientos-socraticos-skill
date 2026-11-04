# RDD — WU-RS3-PINNED-SOURCE-EVIDENCE-023

El candidato inicial `sha256:bcf1cbc6c6439debbb291560eb33229c56a3cd071c066ea5f064ab3e65dbb329`
recibió R3-001 (fiabilidad, crítico): un offset final mayor que el blob podía
pasar por el truncamiento implícito de slices de Python. No se publicó ese
candidato. En lineage `review-507f260c10f66e5b`, Gentle AI validó la
corrección acotada, aprobó y reconoció el candidato final staged
`sha256:6a42c4b652c061ff17c935b385a40378382868038ed9bcfac54a326378fe4773`.
La revisión de cuatro lentes y su validación dirigida fueron estáticas; no
ejecutaron las pruebas de forma independiente.

RED inicial: los controles positivos fallaron con flags desconocidos. RED del
hallazgo: cita autoconsistente con offset fuera del blob devolvió exit 0 en vez
de 2. GREEN final: tres pruebas focales, exit 0. Regresión local final:
`ci/run_quality.sh`, exit 0; 55 CI, 130 supervisor, 62 QA y 367 requisitos.

El commit fijado permite comprobar bytes exactos de una cita. No autentica
autoría, intención humana ni significado; tampoco es una garantía de aislamiento
físico frente a modificación adversarial del almacén Git por el mismo UID.
No se ejecutó calibración en el hardware objetivo. Este recibo es posterior
al candidato revisado.
