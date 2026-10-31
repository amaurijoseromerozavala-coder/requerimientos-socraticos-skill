# Consentimiento RDD por partes

El candidato original fue autorizado por el humano, pero Gentle AI devolvió
`lens_context_budget_exceeded`; no inició revisión ni creó aprobación. No reintentar
el mismo candidato. Se preparan cinco candidatos exactos, sin omitir archivos.
El PRD canónico solo se compactó en whitespace: mismo JSON y digest semántico.

| Parte | Archivos | Líneas | Identidad |
|---|---:|---:|---|
| core | 7 | 890 | `sha256:244addaaaec7698302eadfa32321262beed5f9c341bb5debcb7bd9fadcb7cdb5` |
| protocol | 8 | 1686 | `sha256:4815366453a183d1de513cebf5c97cd96582c147652da479f6d69b20fec3c487` |
| interview | 23 | 738 | `sha256:55a0dc546e2a860a42b1d2c389f948ed403aea8c82d070adeaf1cef856a6a011` |
| evidence | 25 | 538 | `sha256:77778c85936cef6f218a7b53540fbdca3c84e348476919278a2fbfa0830f1ec2` |
| canonical | 1 | 1 | `sha256:709145f50fc44cae5a2a573df58f99ee6509865996a11a8fc22d5d60953f5f11` |

Todos riesgo medio. Conceder cubre solo estos cinco candidatos; no cambios futuros
ni implementación/producción. Omitir no apaga RDD. La revisión conjunta sigue
pendiente: ningún resultado parcial equivale a aprobación integral. Incluso una
parte podría volver a superar el presupuesto; no se garantiza admisión.

Regla workflow.md: «Reenvía el consentimiento si el binario lo exige».
Invocaciones exactas: part-*/consent.json. Cobertura de archivos: review-partition.json.
