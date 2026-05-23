# Sistema de Migraciones de Base de Datos

## 📊 Versionado de Base de Datos

Voxeprint 3D usa un sistema de versionado semántico para la base de datos:

```
voxeprint_X.Y.db
          │ │
          │ └─ Versión Minor: Cambios compatibles (nuevas columnas, comportamiento)
          └─── Versión Major: Cambios incompatibles (columnas eliminadas, estructura)
```

### Versiones Actuales

| Versión BD | Versión App | Schema | Fecha | Cambios Principales |
|---|---|---|---|---|
| 1.1 | 1.1.6+ | 1 | Nov 2025 | Timestamps en hora local |
| 1.0 | 1.0.0 - 1.1.5 | 1 | Oct 2025 | Versión inicial |

## 🔄 Migración v1.0 → v1.1

### ¿Qué cambió?

**v1.0:** Timestamps usaban UTC (3 horas adelante)
```sql
created_at: 2025-11-07 02:24:33  (UTC)
Real:       2025-11-06 23:24:33  (Paraguay)
```

**v1.1:** Timestamps usan hora local de Paraguay
```sql
created_at: 2025-11-06 23:24:33  (Local)
Real:       2025-11-06 23:24:33  ✅
```

### ¿Es necesario migrar?

**NO es obligatorio** - Tu BD v1.0 seguirá funcionando con la app v1.1.6+

**Pero es recomendable** si quieres:
- ✅ Corregir las fechas antiguas (restar 3 horas)
- ✅ Tener consistencia entre registros viejos y nuevos
- ✅ Evitar confusión con fechas "del futuro"

### ¿Qué se migra?

- Tabla `quotes`: created_at, updated_at
- Tabla `customers`: created_at, updated_at
- Tabla `printers`: created_at, updated_at
- Tabla `filaments`: created_at, updated_at
- Tabla `system_configs`: created_at, updated_at

**Total:** Todos los timestamps se ajustan restando 3 horas (UTC-3)

## 🚀 Cómo Migrar

### Opción 1: Migración Automática (Recomendada)

```bash
cd "c:\Users\Zerou\Desarrollo de Programas\Voxeprint---3Dprint-Calculator"
python -m infrastructure.database.migrations.migrate_v1_0_to_v1_1
```

**Qué hace:**
1. ✅ Crea backup automático en `Database/backups/`
2. ✅ Corrige todos los timestamps (UTC → Local)
3. ✅ Crea nueva BD: `voxeprint_1.1.db`
4. ✅ Mantiene `voxeprint_1.0.db` como respaldo

### Opción 2: Solo Triggers (Sin corregir antiguos)

Si quieres que solo los **nuevos** registros usen hora local:

```bash
python tools/migrate_timestamps.py
```

**Qué hace:**
1. ✅ Actualiza triggers a hora local
2. ⏭️  NO corrige registros antiguos
3. ⏭️  NO crea nueva versión de BD

## 📁 Estructura de Archivos

```
Documents/
└── Voxeprint3D/
    └── Database/
        ├── voxeprint_1.0.db          ← BD original (respaldo)
        ├── voxeprint_1.1.db          ← BD nueva (activa)
        └── backups/
            └── voxeprint_1.0_pre_migration_YYYYMMDD_HHMMSS.db
```

## ⚠️ Importante

### Antes de Migrar

1. **Cierra la aplicación** - No migrar con la app abierta
2. **Backup manual** (opcional) - Copia `voxeprint_1.0.db` a lugar seguro
3. **Espacio en disco** - Verifica que hay espacio (BD se duplica)

### Después de Migrar

1. **Verifica las fechas** - Abre la app y revisa presupuestos antiguos
2. **Si todo está bien** - Puedes eliminar `voxeprint_1.0.db`
3. **Si algo salió mal** - Restaura desde `backups/`

## 🔙 Rollback (Deshacer Migración)

Si algo sale mal, puedes restaurar:

### Opción 1: Restaurar desde backup

```bash
cd Documents/Voxeprint3D/Database
copy backups\voxeprint_1.0_pre_migration_*.db voxeprint_1.1.db
```

### Opción 2: Volver a v1.0

```bash
cd Documents/Voxeprint3D/Database
copy voxeprint_1.0.db voxeprint.db
```

Luego en `config/build_config.py`:
```python
current_version: str = "1.0"  # Cambiar de 1.1 a 1.0
```

## 🧪 Testing

Verifica que la migración funcionó:

```bash
# Test básico de timestamps
python tools/test_timestamp.py

# Test de persistencia
python tools/test_quote_save.py
```

## 📌 Preguntas Frecuentes

### ¿Por qué había 3 horas de diferencia?

SQLite usa `CURRENT_TIMESTAMP` que devuelve UTC por defecto. Paraguay está en UTC-3, entonces había +3 horas de desfase.

### ¿Se pierden datos en la migración?

NO. Solo se ajustan las fechas, ningún dato se elimina. Además se crea backup automático.

### ¿Qué pasa si tengo presupuestos nuevos después de migrar?

Los nuevos presupuestos usarán automáticamente hora local. No necesitas hacer nada.

### ¿Puedo usar BD v1.0 con app v1.1.6?

SÍ. Es compatible hacia atrás. Pero los nuevos registros se crearán con hora local.

### ¿Cuánto tarda la migración?

Depende del número de registros:
- < 100 registros: Segundos
- 100-1000 registros: < 1 minuto
- > 1000 registros: 1-2 minutos

### ¿Necesito permisos de administrador?

NO para la migración básica. Solo para instalación/actualización de la app.

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs en `logs/`
2. Verifica que el backup existe en `Database/backups/`
3. Restaura desde backup si es necesario
4. Contacta soporte con el mensaje de error

## 📝 Changelog de Migraciones

### v1.0 → v1.1 (Nov 2025)

**Cambios:**
- Timestamps UTC → Hora local
- Autocommit inmediato
- Triggers actualizados

**Impacto:**
- Fechas ahora muestran hora de Paraguay
- No más desfase de 3 horas
- Persistencia inmediata sin reiniciar app

**Compatibilidad:**
- ✅ BD v1.0 funciona con código v1.1
- ✅ Migración opcional (recomendada)
- ✅ Rollback disponible
