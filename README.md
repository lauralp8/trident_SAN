# Generador de Configuración NetApp Trident SAN

## Descripción General

Herramienta Python para la generación automatizada de archivos de configuración YAML para NetApp Trident CSI en entornos OpenShift y Kubernetes. Este generador implementa validación automática, valores predeterminados optimizados y generación de configuraciones estandarizadas para backends de almacenamiento ONTAP SAN.

**Versión:** 2.0  
**Autor:** PS NetApp

---

## Características Principales

- **Validación automática**: Verifica campos obligatorios antes de la generación
- **Configuración simplificada**: Solo 5 campos obligatorios requeridos
- **Valores predeterminados optimizados**: Configuraciones seguras basadas en mejores prácticas de NetApp
- **Auto-generación de nombres**: Generación automática de `backendName` basado en dataLIF
- **Arquitectura modular**: Código basado en dataclasses de Python con tipado fuerte
- **Documentación inline**: Campos vacíos comentados automáticamente en YAML de salida

---

## Archivos Generados
`backend_storage.yaml` = Configuración principal de TridentBackendConfig + StorageClass de Kubernetes |
`secret.yaml` = (Opcional) Credenciales de Secret de Kubernetes - Solo se genera si especificas username/password en config.yaml

**IMPORTANTE:** Por seguridad, se recomienda crear el Secret directamente en Kubernetes en lugar de 
especificar las credenciales en config.yaml. El backend solo necesita referenciar el nombre del Secret. 

---

## Instalación

### Requisitos Previos

- Python 3.7 o superior
- Acceso a repositorio Git 

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias:**
- `PyYAML>=6.0`

---

## Guía de Inicio Rápido

### Paso 1: Configuración Mínima

Edite el archivo `config.yaml` con los siguientes campos obligatorios:

```yaml
backend:
  managementLIF: 192.168.204.203
  dataLIF: 192.168.205.203
  svm: SVM-SAN-01
  credentials:
    name: trident-creds

storageClass:
  name: ontap-san-storage
```

**NOTA:** Las credenciales (username/password) se configuran de forma SEPARADA en Kubernetes 
mediante un Secret. El backend solo referencia el nombre del Secret mediante `credentials.name`.

### Paso 2: Ejecución del Generador

```bash
python generate_trident_san.py
```

### Paso 3: Verificación de Archivos

El script generará dos archivos en el directorio actual:
- `backend_storage.yaml`
- `secret.yaml`

---

## Referencia Completa de Configuración

### Campos Obligatorios

Los siguientes campos **deben** estar presentes en `config.yaml`:
Backend:
- `managementLIF` Dirección IP de gestión del SVM 
- `dataLIF` Dirección IP de datos iSCSI 
- `svm` Nombre de la Storage Virtual Machine
- `credentials.name` Nombre del Secret de Kubernetes que contiene las credenciales

**NOTA:** El Secret debe existir en Kubernetes antes de desplegar el backend, o puede ser creado 
después del backend pero antes de aprovisionar volúmenes.

**IMPORTANTE:** Las credenciales (username/password) NO se incluyen en config.yaml por seguridad. 
Se crean de forma independiente en Kubernetes como Secret.

---

## Configuración Detallada del Backend

### Sección: backend

#### Parámetros de Conexión (Obligatorios)

```yaml
backend:
  managementLIF: 192.168.204.203  # OBLIGATORIO
  dataLIF: 192.168.205.203        # OBLIGATORIO
  svm: SVM-SAN-01                 # OBLIGATORIO
  credentials:                    # OBLIGATORIO
    name: trident-creds           # Nombre del Secret en Kubernetes
```

#### Parámetros Generales del Backend

```yaml
backend:
  name: backend-san-01            # Opcional
  storagePrefix: trident          # Opcional
  credentialsName: trident-creds  # Opcional
  useCHAP: false                  # Opcional
  chapInitiatorSecret: ""         # Obligatorio si useCHAP=true
  chapTargetInitiatorSecret: ""   # Obligatorio si useCHAP=true
  chapUserName: ""                # Obligatorio si useCHAP=true
  chapTargetUsername: ""          # Obligatorio si useCHAP=true
  aggregate: ""                   # Opcional
  lunsPerFlexvol: "100"           # Opcional
  sanType: iscsi                  # Opcional
  formatOptions: ""               # Opcional
  limitAggregateUsage: ""         # Opcional
  limitVolumeSize: ""             # Opcional
  limitVolumePoolSize: ""         # Opcional
  denyNewVolumePools: "false"     # Opcional
  clientCertificate: ""           # Opcional - Validación SSL/TLS (NO es autenticación)
  clientPrivateKey: ""            # Opcional - Validación SSL/TLS (NO es autenticación)
  trustedCACertificate: ""        # Opcional - Validación SSL/TLS (NO es autenticación)
  labels: ""                      # Opcional
  debugTraceFlags:
    api: false                    # Opcional
    method: false                 # Opcional
  defaults:
    spaceReserve: none
    spaceAllocation: "true"
    snapshotPolicy: none
    snapshotReserve: "0"
    encryption: "false"
    qosPolicy: ""
    adaptiveQosPolicy: ""
    tieringPolicy: none
    luksEncryption: ""
    nameTemplate: ""
```

### Validación de Certificados SSL/TLS (backend)

```yaml
backend:
  clientCertificate: ""           # Opcional
  clientPrivateKey: ""            # Opcional
  trustedCACertificate: ""        # Opcional
```

---

## Configuración del StorageClass

### Sección: storageClass

```yaml
storageClass:
  name: ontap-san-storage         # OBLIGATORIO (debe tener valor)
  isDefault: true                 # Opcional
  syncWave: "5"                   # Opcional
  parameters:
    backendType: ontap-san
    fsType: ext4
    provisioningType: thin
    snapshots: "true"
```

## Configuración de Credenciales

### Creación del Secret en Kubernetes

**Método Recomendado:** Crear el Secret directamente en Kubernetes sin guardarlo en archivos:

```bash
kubectl create secret generic trident-creds \
  --from-literal=username=vsadmin \
  --from-literal=password=NetApp123 \
  -n trident
```

### Generación Automática (Opcional)

Si prefieres que el script genere el archivo secret.yaml, puedes agregar una sección `secret` 
en config.yaml (NO RECOMENDADO por temas de seguridad):

```yaml
secret:
  username: vsadmin
  password: NetApp123
  name: trident-creds  # Debe coincidir con backend.credentials.name
```

## Procedimiento de Desplie

### Paso 1: Generación de Archivos

```bash
# Ejecutar el generador
python generate_trident_san.py
```

Salida esperada:
```
Usando configuración: config.yaml
✓ Archivo generado: backend_storage.yaml
✓ Archivo generado: secret.yaml

¡Archivos YAML generados exitosamente!

Para personalizar:
  1. Edita config.yaml
  2. Ejecuta: python generate_trident_nas.py
```

### Paso 2: Revisión de Archivos Generados

Revisar los archivos generados antes de aplicarlos:

```bash
# Ver contenido del backend
cat backend_storage.yaml

# Ver contenido del secret
cat secret.yaml
```
---

## Resolución de Problemas

### Error: "Los siguientes campos son obligatorios"

**Síntoma:**
```
ERROR: Los siguientes campos son obligatorios en config.yaml:
  - backend.managementLIF
  - backend.dataLIF
  - backend.svm
  - secret.username
  - secret.password
```

**Causa:** Falta uno o más campos obligatorios en `config.yaml`.

**Solución:**
1. Abrir `config.yaml`
2. Verificar que los 5 campos obligatorios tengan valores (no vacíos):
   - `backend.managementLIF`
   - `backend.dataLIF`
   - `backend.svm`
   - `secret.username`
   - `secret.password`

### Error: "FileNotFoundError: config.yaml"

**Síntoma:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'config.yaml'
```

**Causa:** El archivo `config.yaml` no existe en el directorio actual.

**Solución:**
```bash
# Verificar que config.yaml existe
ls -l config.yaml

# Si no existe, crearlo con configuración mínima
cat > config.yaml <<EOF
backend:
  managementLIF: 192.168.1.100
  dataLIF: 192.168.1.101
  svm: svm-nas-01

storageClass:
  name: netapp-nas

secret:
  username: vsadmin
  password: NetApp123
EOF
```

### Backend en Estado "Failed" o "Unknown"

**Síntoma:**
```bash
oc get tbc
NAME                 BACKEND NAME              BACKEND UUID   PHASE    STATUS
backend-nas-01       ontap-nas_192_168_1_101   -              Failed   ...
```

**Causas Posibles:**

1. **Credenciales incorrectas:**
   - Verificar usuario y contraseña en el Secret
   - Verificar permisos del usuario en ONTAP

2. **Conectividad de red:**
   ```bash
   # Desde un pod en el cluster, verificar conectividad
   oc run -it --rm debug --image=busybox --restart=Never -- ping <managementLIF>
   ```

3. **SVM no existe o está detenida:**
   ```bash
   # En ONTAP CLI:
   vserver show -vserver <nombre-svm>
   ```

4. **Política de exportación NFS incorrecta:**
   - Si `autoExportPolicy: false`, verificar que la política especificada en `defaults.exportPolicy` existe
   - Verificar reglas de la política de exportación


### PVC en Estado "Pending"

**Síntoma:**
```bash
oc get pvc
NAME       STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS
test-pvc   Pending   -        -          -              netapp-nas
```

**Causas Posibles:**

1. **Backend no disponible:**
   ```bash
   oc get tbc
   # Verificar que Phase: Bound
   ```

2. **StorageClass no existe:**
   ```bash
   oc get sc
   # Verificar que el SC especificado en el PVC existe
   ```

3. **Límites de cuota excedidos:**
   - Verificar `limitAggregateUsage` y `limitVolumeSize` en config


### Campos Vacíos Comentados en YAML Generado

**Síntoma:**
Los archivos generados tienen líneas comentadas como:
```yaml
# labels: ''
# qosPolicy: ''
```

**Causa:** Comportamiento normal del generador.

**Explicación:**
- Los campos con valores vacíos (`''`) se comentan automáticamente
- Esto mantiene la documentación visible sin afectar la funcionalidad
- Facilita personalización futura descomentando la línea y añadiendo un valor

---

## Referencia Rápida de Valores

### Campos Obligatorios (5 total)

| Campo | Sección | Ejemplo |
|-------|---------|---------|
| `managementLIF` | backend | `192.168.1.100` |
| `dataLIF` | backend | `192.168.1.101` |
| `svm` | backend | `svm-nas-01` |
| `username` | secret | `vsadmin` |
| `password` | secret | `NetApp123` |

### Valores Recomendados para Producción

| Parámetro | Valor Recomendado | Justificación |
|-----------|-------------------|---------------|
| `unixPermissions` | `"755"` | Seguridad: solo propietario puede escribir |
| `snapshotPolicy` | `daily` o `hourly` | Protección de datos |
| `snapshotReserve` | `"5"` a `"10"` | Balance entre protección y capacidad |
| `encryption` | `"true"` | Seguridad (requiere licencia NVE) |
| `autoExportPolicy` | `true` | Automatización, menos configuración manual |
| `limitAggregateUsage` | `"80%"` a `"90%"` | Prevenir llenado completo del agregado |
| `limitVolumeSize` | `"500Gi"` a `"1Ti"` | Prevenir volúmenes excesivamente grandes |

---


## Arquitectura del Código

El generador utiliza una arquitectura modular basada en dataclasses de Python:

### Dataclasses Principales

```python
@dataclass
class BackendConfig:
    """Configuración del TridentBackendConfig"""
    # Campos obligatorios
    managementLIF: str = ''
    dataLIF: str = ''
    svm: str = ''
    # Campos opcionales con valores por defecto
    name: str = 'backend-jc-nas1200'
    storagePrefix: str = 'trident'
    ...

@dataclass
class StorageClassConfig:
    """Configuración del StorageClass de Kubernetes"""
    name: str = 'rhoso-nas'
    isDefault: bool = True
    ...

@dataclass
class SecretConfig:
    """Credenciales de acceso al SVM"""
    name: str = 'trident-creds'
    username: str = ''  # Obligatorio
    password: str = ''  # Obligatorio
```

### Flujo de Procesamiento

1. **load_config()**
   - Lee `config.yaml`
   - Fusiona con valores por defecto
   - Valida campos obligatorios
   - Retorna objeto `TridentConfig`

2. **create_backend_yaml()**
   - Genera diccionario de TridentBackendConfig
   - Auto-genera `backendName` desde `dataLIF`
   - Inyecta campos estáticos (storageDriverName, etc.)

3. **create_storage_class_yaml()**
   - Genera diccionario de StorageClass
   - Configura annotations de K8s

4. **create_secret_yaml()**
   - Genera diccionario de Secret
   - Formatea credenciales en stringData

5. **comment_empty_fields()**
   - Post-procesa YAML generado
   - Comenta campos con valores vacíos
   - Preserva documentación

6. **generate_trident_files()**
   - Orquesta todo el proceso
   - Escribe archivos de salida
   - Muestra confirmación

---

## Seguridad y Mejores Prácticas

### Gestión de Credenciales

1. **No versionar credenciales en Git:**
   ```bash
   # Añadir a .gitignore
   echo "secret.yaml" >> .gitignore
   echo "config.yaml" >> .gitignore  # Si contiene credenciales reales
   ```
---

## Soporte y Documentación Adicional

### Documentación Oficial de NetApp
RELLENAR

### Documentación de Kubernetes
RELLENAR

---

## Contacto y Soporte

Para soporte técnico o consultas:

- **Documentación NetApp:** docs.netapp.com
- **Documentación Parametrización Rhoso:** pdf.ParametrizaciónRhoso
- **Soporte NetApp:** Contactar con su Partner o Representante de NetApp

---

**Última actualización:** Febrero 2026  
**Versión del generador:** 2.0
