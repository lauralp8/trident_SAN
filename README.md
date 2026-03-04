# Generador de Configuración NetApp Trident SAN

## Descripción General

Herramienta Python profesional para la generación automatizada y estandarizada de archivos de configuración YAML para NetApp Trident CSI en entornos Kubernetes y OpenShift. Este generador implementa validación automática de campos obligatorios, valores predeterminados optimizados según mejores prácticas de NetApp, y generación de configuraciones seguras para backends de almacenamiento ONTAP SAN con protocolo iSCSI.

El generador abstrae la complejidad de la configuración manual de Trident, proporcionando una interfaz simplificada basada en un archivo de configuración único (config.yaml) que permite desplegar backends de almacenamiento empresarial de forma rápida y segura.

**Versión:** 2.0  
**Autor:** Professional Services NetApp  
**Última actualización:** Marzo 2026

---

## Tabla de Contenidos

1. [Descripción Funcional](#descripción-funcional)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Creación de Archivos de Configuración desde Cero](#creación-de-archivos-de-configuración-desde-cero)
5. [Guía de Uso](#guía-de-uso)
6. [Parametrización Detallada](#parametrización-detallada)
7. [Flujo Interno del Proceso](#flujo-interno-del-proceso)
8. [Archivos Generados](#archivos-generados)
9. [Gestión de Credenciales y Secret](#gestión-de-credenciales-y-secret)
10. [Logs y Salidas del Sistema](#logs-y-salidas-del-sistema)
11. [Catálogo de Errores](#catálogo-de-errores)
12. [Consideraciones de Seguridad](#consideraciones-de-seguridad)
13. [Mejores Prácticas](#mejores-prácticas)
14. [Resolución de Problemas](#resolución-de-problemas)
15. [Referencias y Documentación](#referencias-y-documentación)

---

## Descripción Funcional

### Propósito y Alcance

Este generador automatiza la creación de recursos Kubernetes necesarios para configurar almacenamiento persistente mediante NetApp Trident en entornos de contenedores. El script procesa un archivo de configuración simplificado y genera dos recursos principales:

1. **TridentBackendConfig**: Define la conexión con el sistema de almacenamiento NetApp ONTAP y los parámetros de aprovisionamiento de volúmenes SAN mediante protocolo iSCSI.

2. **StorageClass**: Define la clase de almacenamiento que los usuarios finales utilizarán para solicitar volúmenes persistentes en sus aplicaciones.

### Funcionalidades Principales

- **Validación Automática**: Verificación de campos obligatorios antes de la generación de archivos.
- **Gestión Segura de Credenciales**: Separación de credenciales sensibles del código de configuración.
- **Auto-generación de Nombres**: Generación automática de identificadores únicos basados en metadatos del backend.
- **Valores Predeterminados Optimizados**: Configuraciones basadas en mejores prácticas de NetApp para entornos de producción.
- **Arquitectura Modular**: Código basado en dataclasses de Python con tipado fuerte para máxima mantenibilidad.
- **Documentación Automática**: Campos vacíos comentados automáticamente en YAML de salida para facilitar personalización futura.
- **Compatibilidad Multi-versión**: Soporte para diferentes versiones de Kubernetes, OpenShift y Trident.

### Arquitectura del Sistema

El generador implementa una arquitectura de tres capas:

1. **Capa de Configuración**: Procesamiento y validación del archivo config.yaml.
2. **Capa de Lógica**: Transformación de configuración en estructuras de datos Python (dataclasses).
3. **Capa de Serialización**: Generación de archivos YAML válidos según especificaciones de Kubernetes y Trident.

---

## Requisitos del Sistema

### Requisitos de Software

#### Obligatorios

| Componente | Versión Requerida | Descripción |
|------------|-------------------|-------------|
| **Python** | 3.9 | Intérprete Python para ejecutar el generador |
| **Kubernetes** | v1.29.4 o compatible | Plataforma de orquestación de contenedores |
| **Trident CSI** | v24.02 o superior | Controlador de almacenamiento de NetApp |
| **kubectl** | v1.29.4 o compatible | Herramienta CLI para interactuar con Kubernetes |
| **PyYAML** | 6.0 o superior | Biblioteca Python para procesamiento YAML |

#### Opcionales

| Componente | Versión Requerida | Descripción |
|------------|-------------------|-------------|
| **OpenShift CLI (oc)** | Compatible con cluster | Solo si se trabaja en entornos OpenShift |
| **Git** | 2.x o superior | Control de versiones para gestión de código |
| **dataclasses-json** | 0.5.8 | Biblioteca para serialización avanzada |

### Requisitos de Infraestructura

- **Sistema de Almacenamiento**: NetApp ONTAP 9.11.1 o superior
- **Protocolo**: iSCSI configurado y accesible desde los nodos de Kubernetes
- **Conectividad de Red**: 
  - Acceso desde nodos de Kubernetes a Management LIF del SVM
  - Acceso desde nodos de Kubernetes a Data LIF del SVM
  - Puertos requeridos: TCP 443 (HTTPS), TCP 3260 (iSCSI)
- **Credenciales**: Usuario con permisos administrativos en el SVM (ejemplo: vsadmin)

### Requisitos de Permisos

- **En Kubernetes/OpenShift**: Permisos para crear recursos en el namespace `trident`
  - Secrets
  - TridentBackendConfig
  - StorageClass

- **En NetApp ONTAP**: 
  - Rol `vsadmin` o superior en el SVM objetivo
  - Permisos para crear volúmenes, LUNs y grupos initiator
  - Acceso a API REST de ONTAP

### Compatibilidad de Versiones

Este generador ha sido probado y validado con las siguientes combinaciones:

| Python | Kubernetes | Trident | ONTAP | Estado |
|--------|-----------|---------|-------|--------|
| 3.9.18 | 1.29.4 | 24.02 | 9.12.x | Validado |
| 3.9.x | 1.28.x | 23.10+ | 9.11.x | Compatible |
| 3.8.x | 1.27.x | 23.04+ | 9.10.x | Compatible |

---

## Instalación y Configuración

### Paso 1: Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd trident_san
```

### Paso 2: Verificar Dependencias del Sistema

```bash
# Verificar versión de Python
python --version
# Debe mostrar: Python 3.9.18 o superior

# Verificar acceso a Kubernetes
kubectl version
# Debe mostrar la versión del cliente y servidor

# Verificar instalación de Trident
kubectl get pods -n trident
# Debe mostrar los pods de Trident en estado Running
```

### Paso 3: Instalar Dependencias de Python

```bash
# Opción 1: Instalación desde requirements.txt (recomendado)
pip install -r requirements.txt

# Opción 2: Instalación manual
pip install PyYAML==6.0
```

### Paso 4: Configurar Variables de Entorno (Opcional)

```bash
export KUBECONFIG=/path/to/kubeconfig
export TRIDENT_NAMESPACE=trident
```

### Paso 5: Verificar Instalación

```bash
# Ejecutar el script con --help
python generate_trident_san.py --help

# Verificar que config.yaml existe
ls -l config.yaml
```

---

## Creación de Archivos de Configuración desde Cero

Esta sección explica cómo crear los archivos de configuración necesarios para el generador desde cero, incluyendo su estructura completa y todos los parámetros disponibles.

### Archivo config.yaml

El archivo `config.yaml` es el archivo principal de configuración que contiene todos los parámetros para el backend de Trident y la StorageClass. A continuación se muestran ejemplos de configuración desde básica hasta completa.

#### Configuración Mínima (Obligatoria)

Esta es la configuración mínima requerida para ejecutar el generador:

```yaml
backend:
  # Conexión a ONTAP (OBLIGATORIOS)
  managementLIF: 192.168.204.203
  dataLIF: 192.168.205.203
  svm: SVM-SAN-01
  
  # Referencia al Secret de Kubernetes (OBLIGATORIO)
  credentials:
    name: trident-creds

storageClass:
  # Nombre de la StorageClass (OBLIGATORIO)
  name: ontap-san-storage
```

#### Configuración Recomendada para Producción

Esta configuración incluye parámetros adicionales recomendados para entornos de producción:

```yaml
backend:
  # Identificación del Recurso Kubernetes
  name: backend-prod-san
  namespace: trident
  
  # Configuración del Backend
  version: 1
  storageDriverName: ontap-san
  backendName: ontap-san-prod
  useREST: true
  
  # Conexión a ONTAP (OBLIGATORIOS)
  managementLIF: 192.168.204.203
  dataLIF: 192.168.205.203
  svm: SVM-SAN-01
  sanType: iscsi
  
  # Credenciales (OBLIGATORIO)
  credentials:
    name: trident-creds
  
  # Configuración de Almacenamiento
  storagePrefix: trident-prod
  lunsPerFlexvol: '100'
  
  # Límites de Recursos
  limitAggregateUsage: '85'
  limitVolumeSize: '500Gi'
  
  # Autenticación CHAP (opcional)
  useCHAP: false
  
  # Valores por Defecto de Volúmenes
  defaults:
    spaceReserve: none
    spaceAllocation: 'true'
    snapshotPolicy: daily
    snapshotReserve: '10'
    encryption: 'false'
    tieringPolicy: none
  
  # Debug (solo para troubleshooting)
  debugTraceFlags:
    api: false
    method: false

storageClass:
  # Identificación
  name: ontap-san-prod
  
  # Comportamiento
  provisioner: csi.trident.netapp.io
  reclaimPolicy: Delete
  volumeBindingMode: Immediate
  allowVolumeExpansion: true
  
  # Anotaciones
  isDefault: false
  
  # Parámetros de Selección
  parameters:
    backendType: ontap-san
    fsType: ext4
    provisioningType: thin
    snapshots: 'true'
```

#### Configuración Completa con Todos los Parámetros

Esta configuración muestra TODOS los parámetros disponibles (muchos son opcionales):

```yaml
backend:
  # Identificación del Recurso Kubernetes
  name: backend-complete-san
  namespace: trident
  
  # Configuración del Backend
  version: 1
  storageDriverName: ontap-san
  backendName: ontap-san-complete
  useREST: true
  
  # Conexión a ONTAP (OBLIGATORIOS)
  managementLIF: 192.168.204.203
  dataLIF: 192.168.205.203
  svm: SVM-SAN-01
  sanType: iscsi
  
  # Credenciales (OBLIGATORIO)
  credentials:
    name: trident-creds
  
  # Configuración de Almacenamiento
  storagePrefix: trident
  aggregate: aggr1_node01
  lunsPerFlexvol: '100'
  denyNewVolumePools: 'false'
  
  # Límites de Recursos
  limitAggregateUsage: '85'
  limitVolumeSize: '1Ti'
  
  # Autenticación CHAP (opcional)
  # IMPORTANTE: Los valores de CHAP van en secret.yaml, NO aquí
  useCHAP: false
  
  # Etiquetas (opcional)
  labels: 'environment=production,tier=gold,department=finance'
  
  # Valores por Defecto de Volúmenes
  defaults:
    spaceReserve: none
    spaceAllocation: 'true'
    snapshotPolicy: none
    snapshotReserve: none
    encryption: 'false'
    qosPolicy: ''
    adaptiveQosPolicy: ''
    tieringPolicy: none
    luksEncryption: ''
    nameTemplate: ''
  
  # Debug (solo para troubleshooting)
  debugTraceFlags:
    api: false
    method: false

storageClass:
  # Identificación
  name: ontap-san-complete
  
  # Comportamiento
  provisioner: csi.trident.netapp.io
  reclaimPolicy: Delete
  volumeBindingMode: Immediate
  allowVolumeExpansion: true
  
  # Anotaciones
  isDefault: false
  syncWave: ''
  
  # Parámetros de Selección
  parameters:
    backendType: ontap-san
    fsType: ext4
    provisioningType: thin
    snapshots: 'true'
```

#### Parámetros Especiales y Consideraciones

**Campos Obligatorios:**
- `backend.managementLIF`
- `backend.svm`
- `backend.credentials.name`
- `storageClass.name`

**Campos Auto-generados:**
Si no se especifican, el generador los creará automáticamente:
- `backend.backendName`: Se genera como `<storageDriverName>_<managementLIF_sanitizada>`
- Ejemplo: `ontap-san_192_168_1_100`

**Forbidden Attributes (IMPORTANTE):**
Los siguientes campos NO deben incluirse en config.yaml, sino en secret.yaml:
- `chapUsername`
- `chapInitiatorSecret`
- `chapTargetUsername`
- `chapTargetInitiatorSecret`
- `clientCertificate`
- `clientPrivateKey`
- `trustedCACertificate`

### Archivo secret.yaml

El archivo `secret.yaml` contiene las credenciales sensibles para autenticarse contra NetApp ONTAP. Este archivo debe crearse manualmente y NUNCA debe subirse a repositorios de código.

**IMPORTANTE: Añadir secret.yaml al .gitignore**

```bash
echo "secret.yaml" >> .gitignore
```

#### Estructura Mínima del Secret

Esta es la estructura mínima requerida para autenticación básica con usuario y contraseña:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: trident-creds
  namespace: trident
type: Opaque
stringData:
  username: vsadmin
  password: NetApp123!
```

**Descripción de Campos:**
- `metadata.name`: Debe coincidir con `backend.credentials.name` en config.yaml (por defecto: `trident-creds`)
- `metadata.namespace`: Debe coincidir con el namespace del backend (por defecto: `trident`)
- `stringData.username`: Usuario administrador del SVM en ONTAP
- `stringData.password`: Contraseña del usuario

#### Secret con Autenticación CHAP

Si en config.yaml se configuró `useCHAP: true`, el secret debe incluir los campos CHAP:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: trident-creds
  namespace: trident
type: Opaque
stringData:
  # Credenciales básicas (OBLIGATORIAS)
  username: vsadmin
  password: NetApp123!
  
  # Autenticación CHAP Bidireccional
  # Nota: Estos valores deben configurarse también en ONTAP
  chapInitiatorSecret: cl9qxWfnUFoinvk4hp1Z
  chapTargetInitiatorSecret: rwbwtuigONgbw9X3rnj
  chapUsername: uh2a1io325bFFILnIk8
  chapTargetUsername: iJF4sgjrnwOwQ2nF1
```

**Generación de Valores CHAP:**

Los valores CHAP deben cumplir estos requisitos:
- **chapUsername y chapTargetUsername**: 12-16 caracteres alfanuméricos
- **chapInitiatorSecret y chapTargetInitiatorSecret**: 12-16 caracteres alfanuméricos

Puede generarlos con:

```bash
# En Linux/macOS
openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -c 16

# En PowerShell (Windows)
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object {[char]$_})
```

**Configuración en ONTAP:**

Después de crear el Secret, debe configurar los mismos valores CHAP en ONTAP:

```bash
# Desde ONTAP CLI
vserver iscsi security create \
  -vserver SVM-SAN-01 \
  -initiator-name <iqn-del-iniciador> \
  -auth-type CHAP \
  -user-name uh2a1io325bFFILnIk8 \
  -inbound-secret cl9qxWfnUFoinvk4hp1Z \
  -outbound-user-name iJF4sgjrnwOwQ2nF1 \
  -outbound-secret rwbwtuigONgbw9X3rnj
```

#### Secret con Autenticación por Certificados

Para autenticación basada en certificados TLS/SSL:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: trident-creds
  namespace: trident
type: Opaque
stringData:
  # Credenciales básicas (pueden omitirse si solo se usa certificados)
  username: vsadmin
  password: NetApp123!
  
  # Certificados en formato Base64
  # Nota: Los certificados deben estar codificados en Base64
  clientCertificate: |
    LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURHVENDQWdHZ0F3SUJBZ0lVQS9i
    OENIOHlyN1VqRzBEN1VoVnRjSHI5VFNjd0RRWUpLb1pJaHZjTkFRRUwKQlFBd0hqRWNN
    Qm9HQTFVRUF3d1RVM1l0VEVGQ0xUTXRVMEZPTFRCMExUQXhNQjRYRFRJeU1EWXlPVEV6
    ...
    (certificado completo en Base64)
    
  clientPrivateKey: |
    LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUV2UUlCQURBTkJna3Foa2lHOXcw
    QkFRRUZBQVNDQktjd2dnU2pBZ0VBQW9JQkFRREQvR1lYc2lNTzZpYzcKdjRRWmxYSEdp
    dVl4WjRhQStadnlWYjcxMEJLL1BSOE5nM1pGMk1PaTdGV01mcWJOREQxWHV1WFhac1ow
    ...
    (clave privada completa en Base64)
    
  trustedCACertificate: |
    LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURYVENDQWtXZ0F3SUJBZ0lVYlFI
    d1lXRDNuU0dsWmM3T1VHTTlCWmxKRnJRd0RRWUpLb1pJaHZjTkFRRUwKQlFBd1BqRVBN
    QTBHQTFVRUF3d0dVazlQVkMxRFFURU1NQW9HQTFVRUN3d0RSRVZXTVEwd0N3WURWUVFL
    ...
    (certificado CA completo en Base64)
```

**Generación de Certificados:**

1. Generar clave privada del cliente:
```bash
openssl genrsa -out client.key 2048
```

2. Generar solicitud de firma de certificado (CSR):
```bash
openssl req -new -key client.key -out client.csr \
  -subj "/CN=trident-client/O=MyOrg/OU=IT"
```

3. Firmar el certificado con la CA de ONTAP:
```bash
# Este paso se realiza en ONTAP o con la CA corporativa
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out client.crt -days 365
```

4. Codificar certificados en Base64:
```bash
# Codificar certificado del cliente
cat client.crt | base64 -w 0

# Codificar clave privada
cat client.key | base64 -w 0

# Codificar certificado CA
cat ca.crt | base64 -w 0
```

#### Secret Completo con Todas las Opciones

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: trident-creds
  namespace: trident
type: Opaque
stringData:
  # Credenciales Básicas (OBLIGATORIAS)
  username: vsadmin
  password: NetApp123!
  
  # Autenticación CHAP (opcional, si useCHAP=true en config.yaml)
  chapInitiatorSecret: cl9qxWfnUFoinvk4hp1Z
  chapTargetInitiatorSecret: rwbwtuigONgbw9X3rnj
  chapUsername: uh2a1io325bFFILnIk8
  chapTargetUsername: iJF4sgjrnwOwQ2nF1
  
  # Certificados TLS/SSL (opcional, para autenticación por certificados)
  # Descomentar y completar si se usa autenticación por certificados
  # clientCertificate: "<certificado-cliente-base64>"
  # clientPrivateKey: "<clave-privada-base64>"
  # trustedCACertificate: "<certificado-ca-base64>"
```

### Creación Paso a Paso

#### Opción 1: Crear config.yaml desde Plantilla

```bash
# Crear config.yaml con configuración mínima
cat > config.yaml <<'EOF'
backend:
  # Conexión a ONTAP (OBLIGATORIOS)
  managementLIF: 192.168.204.203
  dataLIF: 192.168.205.203
  svm: SVM-SAN-01
  
  # Referencia al Secret de Kubernetes (OBLIGATORIO)
  credentials:
    name: trident-creds

storageClass:
  # Nombre de la StorageClass (OBLIGATORIO)
  name: ontap-san-storage
EOF

# Editar el archivo para personalizar los valores
nano config.yaml
# o
vim config.yaml
```

#### Opción 2: Crear secret.yaml desde Plantilla

```bash
# Crear secret.yaml con configuración básica
cat > secret.yaml <<'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: trident-creds
  namespace: trident
type: Opaque
stringData:
  username: vsadmin
  password: CAMBIAR_ESTO
EOF

# IMPORTANTE: Editar y cambiar la contraseña
nano secret.yaml

# IMPORTANTE: Añadir al .gitignore
echo "secret.yaml" >> .gitignore
```

#### Opción 3: Crear Secret Directamente en Kubernetes (Más Seguro)

En lugar de crear un archivo secret.yaml, se recomienda crear el Secret directamente:

```bash
# Sin CHAP
kubectl create secret generic trident-creds \
  --from-literal=username=vsadmin \
  --from-literal=password=NetApp123! \
  -n trident

# Con CHAP
kubectl create secret generic trident-creds \
  --from-literal=username=vsadmin \
  --from-literal=password=NetApp123! \
  --from-literal=chapInitiatorSecret=cl9qxWfnUFoinvk4hp1Z \
  --from-literal=chapTargetInitiatorSecret=rwbwtuigONgbw9X3rnj \
  --from-literal=chapUsername=uh2a1io325bFFILnIk8 \
  --from-literal=chapTargetUsername=iJF4sgjrnwOwQ2nF1 \
  -n trident
```

### Validación de los Archivos

Después de crear los archivos, validar su sintaxis:

```bash
# Validar sintaxis YAML de config.yaml
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Si no hay errores, no mostrará nada
# Si hay errores, mostrará el problema

# Validar sintaxis YAML de secret.yaml (si existe)
python -c "import yaml; yaml.safe_load(open('secret.yaml'))"
```

### Resumen del Flujo Completo

1. **Crear config.yaml** con configuración del backend y StorageClass
2. **Crear secret.yaml** O crear Secret directamente en Kubernetes
3. **Validar** sintaxis YAML de ambos archivos
4. **Ejecutar generador**: `python generate_trident_san.py`
5. **Aplicar Secret** (si se usó secret.yaml): `kubectl apply -f secret.yaml -n trident`
6. **Aplicar backend**: `kubectl apply -f backend_storage_san.yaml -n trident`
7. **Verificar**: `kubectl get tbc -n trident`

---

## Guía de Uso

### Configuración Básica

#### Paso 1: Editar config.yaml

Edite el archivo `config.yaml` con los parámetros mínimos obligatorios:

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

#### Paso 2: Ejecutar el Generador

```bash
python generate_trident_san.py
```

**Salida Esperada:**

```
Usando configuración: config.yaml
Archivo generado: backend_storage_san.yaml

 ------------------------------------------------------------------

 Instrucciones:
  1. Edita config.yaml y secret.yaml
  2. Ejecuta: python generate_trident_nas.py
  3. Aplica los archivos generados en tu clúster:
     - kubectl apply -f secret.yaml -n trident
     - kubectl apply -f backend_storage_san.yaml -n trident
  4. Verifica los recursos creados:
     - kubectl get tridentbackendconfig -n trident

 ------------------------------------------------------------------
```

#### Paso 3: Crear el Secret de Credenciales

**IMPORTANTE**: El Secret debe crearse antes de aplicar el backend.

```bash
kubectl create secret generic trident-creds \
  --from-literal=username=vsadmin \
  --from-literal=password=NetApp123! \
  -n trident
```

#### Paso 4: Aplicar el Backend y StorageClass

```bash
# Aplicar el backend
kubectl apply -f backend_storage_san.yaml -n trident

# Verificar el estado del backend
kubectl get tridentbackendconfig -n trident

# Verificar el StorageClass
kubectl get storageclass
```

#### Paso 5: Validar el Despliegue

```bash
# Verificar que el backend está en estado Bound
kubectl get tbc -n trident
# Esperar a que Phase: Bound

# Verificar logs de Trident (si hay problemas)
kubectl logs -n trident -l app=trident-csi --tail=100
```

---

## Parametrización Detallada

### Backend Configuration

#### Identificación del Recurso Kubernetes

| Parámetro | Valor | Modificable | Descripción |
|-----------|-------|-------------|-------------|
| `apiVersion` | `trident.netapp.io/v1` | No | Versión de la API de Trident CRD |
| `kind` | `TridentBackendConfig` | No | Tipo de recurso Kubernetes |
| `namespace` | `trident` | Sí | Namespace donde se despliega el backend |

#### Configuración del Backend

| Parámetro | Valor por Defecto | Obligatorio | Descripción |
|-----------|-------------------|-------------|-------------|
| `version` | `1` | Sí | Versión del esquema de configuración |
| `storageDriverName` | `ontap-san` | Sí | Driver de almacenamiento de Trident |
| `backendName` | `<driverName>_<managementLIF>` | No | Nombre del backend (auto-generado si no se especifica) |
| `sanType` | `iscsi` | Sí | Protocolo SAN a utilizar |
| `useREST` | `true` | Sí | Utilizar API REST de ONTAP |

#### Conexión a NetApp ONTAP (Obligatorios)

| Parámetro | Ejemplo | Obligatorio | Descripción |
|-----------|---------|-------------|-------------|
| `managementLIF` | `192.168.1.100` | Sí | IP de gestión del SVM |
| `dataLIF` | `192.168.1.101` | No | IP de datos para conexiones iSCSI (opcional) |
| `svm` | `svm-san-01` | Sí | Storage Virtual Machine en ONTAP |

#### Autenticación

| Parámetro | Valor por Defecto | Ubicación | Descripción |
|-----------|-------------------|-----------|-------------|
| `credentials.name` | `trident-creds` | config.yaml | Nombre del Secret en Kubernetes |
| `username` | - | secret.yaml | Usuario administrador del SVM |
| `password` | - | secret.yaml | Contraseña del usuario |
| `useCHAP` | `false` | config.yaml | Habilitar autenticación CHAP |
| `chapInitiatorSecret` | `""` | secret.yaml | Secret del iniciador CHAP |
| `chapTargetInitiatorSecret` | `""` | secret.yaml | Secret del target iniciador CHAP |
| `chapUsername` | `""` | secret.yaml | Usuario CHAP |
| `chapTargetUsername` | `""` | secret.yaml | Usuario CHAP del target |
| `clientCertificate` | `""` | secret.yaml | Certificado cliente (Base64) |
| `clientPrivateKey` | `""` | secret.yaml | Clave privada cliente (Base64) |
| `trustedCACertificate` | `""` | secret.yaml | Certificado CA (Base64) |

**IMPORTANTE**: Los campos de autenticación CHAP y certificados son "forbidden attributes" en el spec del TridentBackendConfig. Deben definirse exclusivamente en el Secret de Kubernetes.

#### Almacenamiento y Recursos

| Parámetro | Valor por Defecto | Descripción |
|-----------|-------------------|-------------|
| `storagePrefix` | `trident` | Prefijo para volúmenes creados |
| `aggregate` | `""` | Agregado específico para aprovisionamiento |
| `limitAggregateUsage` | `""` | Límite de uso del agregado (porcentaje) |
| `limitVolumeSize` | `""` | Tamaño máximo de volumen permitido |
| `lunsPerFlexvol` | `100` | Número máximo de LUNs por FlexVol |

#### Valores por Defecto de Volúmenes (defaults)

| Parámetro | Valor por Defecto | Descripción |
|-----------|-------------------|-------------|
| `spaceReserve` | `none` | Reserva de espacio (none/volume) |
| `spaceAllocation` | `true` | Asignación de espacio para LUNs |
| `snapshotPolicy` | `none` | Política de snapshots |
| `snapshotReserve` | `none` | Reserva para snapshots |
| `encryption` | `false` | Habilitar cifrado de volumen (NVE) |
| `qosPolicy` | `""` | Grupo de políticas QoS |
| `adaptiveQosPolicy` | `""` | Grupo de políticas QoS adaptativas |
| `tieringPolicy` | `none` | Política de tiering de datos |
| `luksEncryption` | `""` | Cifrado LUKS |
| `nameTemplate` | `""` | Plantilla para nombres de volumen |

#### Debug y Depuración

| Parámetro | Valor por Defecto | Descripción |
|-----------|-------------------|-------------|
| `debugTraceFlags.api` | `false` | Traza llamadas a API de ONTAP |
| `debugTraceFlags.method` | `false` | Traza métodos internos de Trident |

### Storage Class Configuration

#### Identificación del Recurso Kubernetes

| Parámetro | Valor | Modificable | Descripción |
|-----------|-------|-------------|-------------|
| `apiVersion` | `storage.k8s.io/v1` | No | Versión de la API de StorageClass |
| `kind` | `StorageClass` | No | Tipo de recurso Kubernetes |

#### Configuración de la Storage Class

| Parámetro | Valor por Defecto | Obligatorio | Descripción |
|-----------|-------------------|-------------|-------------|
| `name` | `rhoso-san` | Sí | Nombre de la StorageClass |
| `provisioner` | `csi.trident.netapp.io` | No (fijo) | Provisioner CSI de Trident |

#### Comportamiento del Storage

| Parámetro | Valor por Defecto | Opciones | Descripción |
|-----------|-------------------|----------|-------------|
| `reclaimPolicy` | `Delete` | Delete/Retain | Política de eliminación de volúmenes |
| `volumeBindingMode` | `Immediate` | Immediate/WaitForFirstConsumer | Modo de binding de volúmenes |
| `allowVolumeExpansion` | `true` | true/false | Permitir expansión de volúmenes |

#### Anotaciones (Annotations)

| Parámetro | Valor por Defecto | Descripción |
|-----------|-------------------|-------------|
| `isDefaultClass` | `false` | Marcar como StorageClass por defecto |
| `syncWave` | `""` | Orden de sincronización para ArgoCD |

#### Parámetros de Selección de Backend

| Parámetro | Valor por Defecto | Descripción |
|-----------|-------------------|-------------|
| `backendType` | `ontap-san` | Tipo de driver de Trident |
| `fsType` | `ext4` | Sistema de archivos (ext4/xfs) |
| `provisioningType` | `thin` | Tipo de aprovisionamiento |
| `snapshots` | `true` | Soporte de snapshots de Kubernetes |

---

## Flujo Interno del Proceso

### Diagrama de Flujo General

```
[Inicio] -> [Cargar config.yaml] -> [Validar campos obligatorios] 
    -> [Fusionar con defaults] -> [Generar TridentBackendConfig] 
    -> [Generar StorageClass] -> [Serializar a YAML] 
    -> [Post-procesamiento] -> [Escribir archivos] -> [Fin]
```

### Flujo Detallado Paso a Paso

#### 1. Inicialización del Sistema

```python
# Punto de entrada
if __name__ == "__main__":
    main()
```

**Operaciones:**
- Verificación de existencia de config.yaml
- Configuración de encoding UTF-8
- Preparación del entorno de ejecución

#### 2. Carga y Parsing de Configuración

```python
def load_config(config_file: str = "config.yaml") -> TridentConfig
```

**Operaciones:**
- Lectura del archivo YAML
- Parsing con PyYAML safe_load
- Conversión a diccionario Python
- Manejo de caracteres Unicode

**Validaciones:**
- Archivo existe y es legible
- YAML es válido sintácticamente
- Estructura contiene secciones requeridas (backend, storageClass)

#### 3. Fusión con Valores por Defecto

```python
def merge_dicts(base: Dict, override: Dict) -> Dict
```

**Operaciones:**
- Fusión recursiva de diccionarios
- Prioridad a valores del usuario sobre defaults
- Preservación de valores anidados
- Manejo de tipos complejos (listas, diccionarios)

#### 4. Construcción de Objetos Dataclass

**Operaciones:**
- Instanciación de BackendDefaults
- Instanciación de DebugTraceFlags
- Instanciación de BackendConfig
- Instanciación de StorageClassParameters
- Instanciación de StorageClassConfig
- Instanciación de SecretConfig

**Validación de Tipos:**
- Verificación de tipos de datos según dataclass
- Conversión automática cuando sea posible
- Error si tipo incompatible

#### 5. Validación de Campos Obligatorios

```python
# Validación de campos backend
errors = []
if not backend_config.managementLIF:
    errors.append("  - backend.managementLIF")
# ...
```

**Validaciones Ejecutadas:**
- backend.managementLIF no vacío
- backend.svm no vacío
- backend.credentials.name no vacío

**Acción si Falla:**
- Acumulación de todos los errores
- Lanzamiento de ValueError con lista completa
- Terminación del script

#### 6. Generación de TridentBackendConfig

```python
def create_backend_yaml(config: BackendConfig, secret_name: str) -> Dict
```

**Operaciones:**
- Conversión de dataclass a diccionario con asdict()
- Extracción de campos para metadata (name, namespace)
- Extracción de campos para spec (version, backendName, etc.)
- Eliminación de campos "forbidden" (CHAP, certificados)
- Auto-generación de backendName si no se especifica
- Construcción de estructura jerárquica YAML
- Inyección de valores estáticos (apiVersion, kind)

**Lógica de backendName:**
```python
if not backend_name_spec:
    mgmt_lif_sanitized = backend['managementLIF'].replace('.', '_')
    backend_name_spec = f"{storage_driver_name}_{mgmt_lif_sanitized}"
```

#### 7. Generación de StorageClass

```python
def create_storage_class_yaml(config: StorageClassConfig) -> Dict
```

**Operaciones:**
- Construcción de metadata con annotations
- Configuración de provisioner
- Definición de reclaimPolicy
- Configuración de parameters de selección
- Configuración de volumeBindingMode
- Configuración de allowVolumeExpansion

#### 8. Generación de Secret (Opcional)

```python
def create_secret_yaml(config: SecretConfig, backend_config: BackendConfig) -> Dict
```

**Operaciones:**
- Creación de estructura base del Secret
- Inclusión de username y password
- Inclusión condicional de campos CHAP (si useCHAP=true)
- Inclusión condicional de certificados (si están definidos)
- Formateo en stringData (sin codificación Base64)

#### 9. Serialización a YAML

```python
yaml.dump(backend, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
```

**Operaciones:**
- Serialización de diccionarios a formato YAML
- Preservación del orden de claves (sort_keys=False)
- Soporte para caracteres Unicode
- Formato legible (default_flow_style=False)
- Separación de recursos con ---

#### 10. Post-procesamiento de YAML

```python
def comment_empty_fields(filepath: str) -> None
```

**Operaciones:**
- Lectura del archivo YAML generado
- Identificación de campos con valores vacíos ('', "")
- Comentado automático de líneas con valores vacíos
- Preservación de campos contenedores (metadata, spec, defaults)
- Reescritura del archivo modificado

**Lógica de Comentado:**
- Campos con valores vacíos: comentados con #
- Campos contenedores: nunca comentados
- Indentación: preservada
- Comentarios existentes: no modificados

#### 11. Escritura de Archivos de Salida

```python
with open(backend_file, 'w', encoding='utf-8') as f:
    yaml.dump(backend, f, ...)
    f.write('\n---\n\n')
    yaml.dump(storage_class, f, ...)
```

**Archivos Generados:**
- backend_storage_san.yaml: Contiene TridentBackendConfig + StorageClass
- secret.yaml: Generado solo si username y password están presentes

#### 12. Presentación de Resultados

**Operaciones:**
- Confirmación de archivos generados
- Instrucciones de uso
- Información sobre el Secret
- Comando para aplicar en Kubernetes

---

## Archivos Generados

### backend_storage_san.yaml

Este archivo contiene dos recursos de Kubernetes separados por `---`:

#### 1. TridentBackendConfig

```yaml
apiVersion: trident.netapp.io/v1
kind: TridentBackendConfig
metadata:
  name: backend-jc-san
  namespace: trident
spec:
  version: 1
  backendName: ontap-san_192_168_205_203
  storageDriverName: ontap-san
  useREST: true
  managementLIF: 192.168.204.203
  dataLIF: 192.168.205.203
  svm: SVM-SAN-01
  storagePrefix: trident
  useCHAP: false
  lunsPerFlexvol: '100'
  sanType: iscsi
  denyNewVolumePools: 'false'
  defaults:
    spaceReserve: none
    spaceAllocation: 'true'
    snapshotPolicy: none
    snapshotReserve: none
    encryption: 'false'
    tieringPolicy: none
  debugTraceFlags:
    api: false
    method: false
  credentials:
    name: trident-creds
```

#### 2. StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ontap-san-storage
  annotations:
    storageclass.kubernetes.io/is-default-class: 'false'
    argocd.argoproj.io/sync-wave: ''
provisioner: csi.trident.netapp.io
reclaimPolicy: Delete
parameters:
  backendType: ontap-san
  fsType: ext4
  provisioningType: thin
  snapshots: 'true'
allowVolumeExpansion: true
volumeBindingMode: Immediate
```

### secret.yaml (Opcional)

El archivo secret.yaml contiene las credenciales necesarias para autenticarse contra el SVM de NetApp ONTAP. Este archivo debe ser creado manualmente antes de aplicar el backend y contiene, como mínimo, dos campos obligatorios dentro de la sección `stringData`: (1) `username` y (2) `password`. El nombre predeterminado del Secret es `trident-creds`, y este debe coincidir con el valor especificado en el campo `credentials.name` dentro del archivo `config.yaml`.

Por motivos de seguridad, las credenciales nunca deben incluirse directamente en el archivo `config.yaml`. Además, el archivo `secret.yaml` debe estar incluido en el `.gitignore` para evitar su exposición accidental en repositorios de código. Se recomienda que el usuario cree este archivo desde cero, siguiendo la estructura propuesta en la documentación.

#### Estructura Básica del Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: trident-creds
type: Opaque
stringData:
  username: vsadmin
  password: NetApp123!
```

#### Estructura Completa con CHAP y Certificados

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: trident-creds
type: Opaque
stringData:
  # Credenciales básicas
  username: vsadmin
  password: NetApp123!
  
  # Campos CHAP (si useCHAP=true)
  chapInitiatorSecret: cl9qxWfnUFoinvk
  chapTargetInitiatorSecret: rwbwtuigONgbw
  chapUsername: uh2a1io325bFFILn
  chapTargetUsername: iJF4sgjrnwOwQ
  
  # Certificados (si se usa autenticación por certificados)
  # clientCertificate: "<certificado-base64>"
  # clientPrivateKey: "<clave-privada-base64>"
  # trustedCACertificate: "<ca-cert-base64>"
```

**IMPORTANTE**: En versiones recientes de Trident con TridentBackendConfig, los campos CHAP y de certificados son "forbidden attributes" en el backend spec y deben definirse exclusivamente en el Secret.

---

## Gestión de Credenciales y Secret

### Creación del Secret en Kubernetes

#### Método 1: Creación Directa (Recomendado)

Este método es el más seguro, ya que las credenciales nunca se almacenan en archivos del sistema de archivos.

```bash
kubectl create secret generic trident-creds \
  --from-literal=username=vsadmin \
  --from-literal=password=NetApp123! \
  -n trident
```

#### Método 2: Creación con CHAP

Si se utiliza autenticación CHAP, incluir los campos adicionales:

```bash
kubectl create secret generic trident-creds \
  --from-literal=username=vsadmin \
  --from-literal=password=NetApp123! \
  --from-literal=chapInitiatorSecret=cl9qxWfnUFoinvk \
  --from-literal=chapTargetInitiatorSecret=rwbwtuigONgbw \
  --from-literal=chapUsername=uh2a1io325bFFILn \
  --from-literal=chapTargetUsername=iJF4sgjrnwOwQ \
  -n trident
```

#### Método 3: Creación desde Archivo

Si es necesario crear el Secret desde un archivo:

```bash
# Crear el archivo secret.yaml manualmente
kubectl apply -f secret.yaml -n trident
```

### Verificación del Secret

```bash
# Verificar que el Secret existe
kubectl get secret trident-creds -n trident

# Ver detalles del Secret (sin mostrar contenido)
kubectl describe secret trident-creds -n trident

# Ver contenido del Secret (decodificado)
kubectl get secret trident-creds -n trident -o jsonpath='{.data.username}' | base64 -d
```

### Actualización del Secret

```bash
# Eliminar el Secret existente
kubectl delete secret trident-creds -n trident

# Crear el nuevo Secret con las credenciales actualizadas
kubectl create secret generic trident-creds \
  --from-literal=username=vsadmin \
  --from-literal=password=NuevaPassword123! \
  -n trident
```

### Rotación de Credenciales

Para rotar credenciales sin interrumpir el servicio:

1. Actualizar credenciales en ONTAP primero
2. Actualizar el Secret en Kubernetes
3. Reiniciar el pod del controlador de Trident (si es necesario)

```bash
# Reiniciar el controlador de Trident
kubectl rollout restart deployment trident-csi -n trident
```

---

## Logs y Salidas del Sistema

### Logs del Script de Generación

#### Salida Normal (Éxito)

```
Usando configuración: config.yaml
Archivo generado: backend_storage_san.yaml

 ------------------------------------------------------------------

 Instrucciones:
  1. Edita config.yaml y secret.yaml
  2. Ejecuta: python generate_trident_nas.py
  3. Aplica los archivos generados en tu clúster:
     - kubectl apply -f secret.yaml -n trident
     - kubectl apply -f backend_storage_san.yaml -n trident
  4. Verifica los recursos creados:
     - kubectl get tridentbackendconfig -n trident

 ------------------------------------------------------------------
```

#### Salida con Advertencia (Secret no generado)

```
Usando configuración: config.yaml
Archivo generado: backend_storage_san.yaml
⚠ Secret no generado (no hay credenciales en config.yaml)
  El backend usará el Secret existente en Kubernetes: 'trident-creds'

Archivo backend_storage_san.yaml correctamente generado para Trident SAN.
```

### Logs de Kubernetes/Trident

#### Verificar Estado del Backend

```bash
# Ver estado del TridentBackendConfig
kubectl get tbc -n trident

# Output esperado:
NAME              BACKEND NAME                      BACKEND UUID                           PHASE   STATUS
backend-jc-san    ontap-san_192_168_205_203        4869e9ee-8e0d-4fbb-99d4-8c7c37c79c31   Bound   Success
```

#### Ver Detalles del Backend

```bash
kubectl describe tbc backend-jc-san -n trident
```

**Salida esperada en caso de éxito:**

```
Name:         backend-jc-san
Namespace:    trident
API Version:  trident.netapp.io/v1
Kind:         TridentBackendConfig
Metadata:
  Creation Timestamp:  2026-03-03T10:00:00Z
Spec:
  Backend Name:         ontap-san_192_168_205_203
  Credentials:
    Name:  trident-creds
  Data LIF:              192.168.205.203
  Management LIF:        192.168.204.203
  Storage Driver Name:   ontap-san
  SVM:                   SVM-SAN-01
  Use REST:              true
Status:
  Backend Info:
    Backend Name:         ontap-san_192_168_205_203
    Backend UUID:         4869e9ee-8e0d-4fbb-99d4-8c7c37c79c31
  Deletion Policy:        delete
  Last Operation Status:  Success
  Message:                Backend 'ontap-san_192_168_205_203' created
  Phase:                  Bound
Events:
  Type    Reason   Age   From                    Message
  ----    ------   ----  ----                    -------
  Normal  Success  1m    trident-crd-controller  Backend 'ontap-san_192_168_205_203' created
```

#### Ver Logs del Controlador de Trident

```bash
# Ver logs en tiempo real
kubectl logs -n trident -l app=trident-csi -f

# Ver últimas 100 líneas
kubectl logs -n trident -l app=trident-csi --tail=100

# Ver logs de un pod específico
kubectl logs -n trident <nombre-del-pod>
```

#### Logs de Aprovisionamiento de Volumen

```bash
# Ver eventos del PVC
kubectl describe pvc <nombre-pvc>

# Ver logs del pod de Node Plugin
kubectl logs -n trident -l app=trident-csi-node
```

### Niveles de Log

| Nivel | Descripción | Uso |
|-------|-------------|-----|
| **INFO** | Información general de operaciones | Operaciones normales |
| **WARNING** | Advertencias no críticas | Problemas potenciales |
| **ERROR** | Errores que requieren atención | Fallos de operación |
| **DEBUG** | Información detallada para depuración | Solo activar cuando se requiera troubleshooting |

### Activar Debug en Trident

Para activar logs de debug en Trident, modificar el backend:

```yaml
debugTraceFlags:
  api: true
  method: true
```

**ADVERTENCIA**: No activar debug en producción, genera gran volumen de logs.

---

## Catálogo de Errores

### Errores de Configuración

#### Error 1: Campos Obligatorios Faltantes

**Mensaje:**
```
ERROR: Los siguientes campos son obligatorios en config.yaml:
  - backend.managementLIF
  - backend.svm
  - backend.credentials.name
```

**Causa:** Uno o más campos obligatorios están vacíos o no definidos en config.yaml.

**Solución:**
1. Abrir config.yaml
2. Verificar que los campos listados tengan valores no vacíos
3. Guardar y ejecutar el script nuevamente

**Ejemplo de Corrección:**
```yaml
backend:
  managementLIF: 192.168.204.203  # Añadir valor (obligatorio)
  svm: SVM-SAN-01                 # Añadir valor (obligatorio)
  credentials:
    name: trident-creds           # Añadir valor (obligatorio)
  dataLIF: 192.168.205.203        # Opcional - IP de datos para iSCSI
```

#### Error 2: Archivo config.yaml No Encontrado

**Mensaje:**
```
ERROR: No se encontró el archivo de configuración.

Crea el archivo:
  - config.yaml
```

**Causa:** El archivo config.yaml no existe en el directorio actual.

**Solución:**
```bash
# Verificar directorio actual
pwd

# Listar archivos
ls -la

# Crear config.yaml con plantilla mínima
cat > config.yaml <<EOF
backend:
  managementLIF: 192.168.1.100
  dataLIF: 192.168.1.101
  svm: svm-san-01
  credentials:
    name: trident-creds

storageClass:
  name: ontap-san-storage
EOF
```

#### Error 3: YAML Inválido

**Mensaje:**
```
yaml.scanner.ScannerError: while scanning a simple key
  in "<unicode string>", line 3, column 1
```

**Causa:** Sintaxis YAML incorrecta en config.yaml.

**Solución:**
1. Verificar indentación (usar espacios, no tabs)
2. Verificar que los dos puntos (:) tengan espacio después
3. Verificar que las comillas estén balanceadas
4. Usar un validador YAML online si es necesario

**Herramientas de Validación:**
```bash
# Validar YAML con Python
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Validar YAML con yamllint (si está instalado)
yamllint config.yaml
```

### Errores de Despliegue en Kubernetes

#### Error 4: Backend en Estado "Failed" - Forbidden Attributes

**Mensaje:**
```
Message: Failed to apply the backend update; 
unsupported config error; 
input contains forbidden attributes: 
[ChapUsername ChapInitiatorSecret ChapTargetUsername ChapTargetInitiatorSecret]
```

**Causa:** Los campos CHAP están definidos en el spec del backend en lugar del Secret.

**Solución:**
1. Eliminar los campos CHAP del config.yaml:
```yaml
backend:
  useCHAP: true
  # NO incluir chapInitiatorSecret
  # NO incluir chapTargetInitiatorSecret
  # NO incluir chapUserName
  # NO incluir chapTargetUsername
```

2. Añadir los campos CHAP al secret.yaml:
```yaml
stringData:
  username: vsadmin
  password: NetApp123!
  chapInitiatorSecret: valor
  chapTargetInitiatorSecret: valor
  chapUsername: valor
  chapTargetUsername: valor
```

3. Actualizar el Secret:
```bash
kubectl delete secret trident-creds -n trident
kubectl apply -f secret.yaml -n trident
```

4. Eliminar y recrear el backend:
```bash
kubectl delete tbc backend-jc-san -n trident
kubectl apply -f backend_storage_san.yaml -n trident
```

#### Error 5: Backend en Estado "Failed" - Credenciales Incorrectas

**Mensaje:**
```
Message: API call failed: authentication failed
```

**Causa:** Las credenciales en el Secret son incorrectas o el usuario no tiene permisos suficientes.

**Solución:**
1. Verificar las credenciales en ONTAP:
```bash
# Desde ONTAP CLI
security login show -vserver <svm-name>
```

2. Probar las credenciales manualmente:
```bash
# Desde un cliente con acceso a ONTAP
curl -k -u vsadmin:password https://<managementLIF>/api/cluster
```

3. Actualizar el Secret con las credenciales correctas

#### Error 6: Backend en Estado "Failed" - Conectividad de Red

**Mensaje:**
```
Message: unable to connect to storage array; 
error: dial tcp 192.168.204.203:443: i/o timeout
```

**Causa:** No hay conectividad de red entre los nodos de Kubernetes y el Management LIF.

**Solución:**
1. Verificar conectividad desde un nodo:
```bash
# Obtener un nodo
kubectl get nodes

# Crear pod de debug en ese nodo
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- /bin/bash

# Dentro del pod, probar conectividad
ping 192.168.204.203
curl -k https://192.168.204.203
```

2. Verificar firewall en ONTAP:
```bash
# Desde ONTAP CLI
network interface show -vserver <svm-name>
network interface show -role data
```

3. Verificar reglas de firewall en Kubernetes

#### Error 7: PVC en Estado "Pending"

**Mensaje:**
```
Events:
  Type     Reason                Age               From                         Message
  ----     ------                ----              ----                         -------
  Warning  ProvisioningFailed    5s (x2 over 15s)  persistentvolume-controller  
  Failed to provision volume: error getting handle for backend ontap-san_192_168_205_203: 
  backend ontap-san_192_168_205_203 not found
```

**Causa:** El backend no está disponible o no existe.

**Solución:**
1. Verificar el estado del backend:
```bash
kubectl get tbc -n trident
```

2. Si el backend no existe, crearlo:
```bash
kubectl apply -f backend_storage_san.yaml -n trident
```

3. Si el backend está en estado Failed, revisar los logs y corregir el problema

4. Esperar a que el backend esté en estado Bound antes de crear PVCs

#### Error 8: PVC en Estado "Pending" - StorageClass No Existe

**Mensaje:**
```
Events:
  Warning  ProvisioningFailed  storageclass.storage.k8s.io "ontap-san-storage" not found
```

**Causa:** La StorageClass especificada en el PVC no existe.

**Solución:**
1. Verificar StorageClasses disponibles:
```bash
kubectl get storageclass
```

2. Aplicar el StorageClass:
```bash
kubectl apply -f backend_storage_san.yaml
```

3. Verificar que el nombre en el PVC coincide con el StorageClass:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
spec:
  storageClassName: ontap-san-storage  # Debe coincidir
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### Errores de Python

#### Error 9: Módulo No Encontrado

**Mensaje:**
```
ModuleNotFoundError: No module named 'yaml'
```

**Causa:** La dependencia PyYAML no está instalada.

**Solución:**
```bash
pip install PyYAML==6.0
# o
pip install -r requirements.txt
```

#### Error 10: Versión de Python Incompatible

**Mensaje:**
```
SyntaxError: invalid syntax
```

**Causa:** Se está usando una versión de Python inferior a 3.7.

**Solución:**
```bash
# Verificar versión
python --version

# Si es inferior a 3.7, instalar Python 3.9 o superior
# Debian/Ubuntu:
sudo apt-get install python3.9

# Red Hat/CentOS:
sudo yum install python39
```

---

## Consideraciones de Seguridad

### Gestión de Credenciales

#### Principios Fundamentales

1. **Separación de Credenciales**: Las credenciales nunca deben almacenarse en archivos de configuración versionados.

2. **Uso de Secrets de Kubernetes**: Utilizar la funcionalidad nativa de Secrets para almacenar información sensible.

3. **Principio de Mínimo Privilegio**: El usuario configurado en el Secret debe tener SOLO los permisos necesarios en ONTAP.

4. **Rotación Regular**: Implementar un proceso de rotación de credenciales periódico.

5. **Auditoría**: Mantener registro de accesos y cambios en las credenciales.

#### Configuración Segura del Usuario en ONTAP

```bash
# Crear un usuario específico para Trident con permisos limitados
security login create -user-or-group-name trident-user \
  -application http \
  -authentication-method password \
  -role vsadmin \
  -vserver SVM-SAN-01

# Configurar expiración de contraseña
security login modify -user-or-group-name trident-user \
  -vserver SVM-SAN-01 \
  -password-expiry-time 90
```

#### Protección de secret.yaml

1. **Añadir a .gitignore**:
```bash
echo "secret.yaml" >> .gitignore
echo "config.yaml" >> .gitignore  # Si contiene datos sensibles
```

2. **Permisos del Archivo**:
```bash
chmod 600 secret.yaml
```

3. **Eliminar Después de Uso**:
```bash
# Después de aplicar el Secret en Kubernetes
rm secret.yaml
```

### Seguridad de Red

#### Segmentación de Red

- **Management Network**: Segregar el tráfico de gestión (Management LIF) en una VLAN separada.
- **Data Network**: Utilizar VLAN dedicada para tráfico iSCSI (Data LIF).
- **Firewall**: Implementar reglas de firewall restrictivas permitiendo solo el tráfico necesario.

#### Puertos Requeridos

| Puerto | Protocolo | Dirección | Descripción |
|--------|-----------|-----------|-------------|
| 443 | TCP | Nodos K8s → Management LIF | HTTPS para API REST de ONTAP |
| 3260 | TCP | Nodos K8s → Data LIF | iSCSI data path |

#### Configuración de Firewall en ONTAP

```bash
# Crear política de firewall para Management LIF
network interface firewall-policy create \
  -policy management-policy \
  -service https \
  -allow-list 192.168.100.0/24

# Aplicar política a la LIF
network interface modify \
  -vserver SVM-SAN-01 \
  -lif sansvm-mgmt \
  -firewall-policy management-policy
```

### Cifrado de Datos

#### Cifrado en Reposo (NetApp Volume Encryption)

Habilitar NVE en el backend:

```yaml
defaults:
  encryption: "true"
```

**Requisitos**:
- Licencia NetApp Volume Encryption (NVE)
- ONTAP 9.1 o superior
- Onboard Key Manager o External Key Manager configurado

#### Cifrado en Tránsito

1. **iSCSI**: El protocolo iSCSI no proporciona cifrado nativo. Para cifrado en tránsito:
   - Utilizar IPsec
   - Utilizar VPN entre nodos K8s y ONTAP
   - Implementar cifrado a nivel de aplicación

2. **CHAP Authentication**: Aunque no es cifrado, proporciona autenticación:

```yaml
backend:
  useCHAP: true
```

**IMPORTANTE**: Los valores CHAP deben definirse en secret.yaml, no en config.yaml.

### Auditoría y Cumplimiento

#### Logs de Auditoría en ONTAP

```bash
# Habilitar auditing en el SVM
vserver audit create \
  -vserver SVM-SAN-01 \
  -destination /audit_log
  
# Verificar configuración
vserver audit show
```

#### Logs de Auditoría en Kubernetes

```bash
# Habilitar audit logging en Kubernetes (requiere configuración del API server)
# Ver eventos de acceso a Secrets
kubectl get events --all-namespaces | grep Secret

# Auditar cambios en TridentBackendConfig
kubectl get events -n trident | grep TridentBackendConfig
```

### RBAC (Role-Based Access Control)

#### Permisos Mínimos Requeridos en Kubernetes

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: trident-backend-manager
  namespace: trident
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list", "create", "update"]
- apiGroups: ["trident.netapp.io"]
  resources: ["tridentbackendconfigs"]
  verbs: ["get", "list", "create", "update", "delete"]
- apiGroups: ["storage.k8s.io"]
  resources: ["storageclasses"]
  verbs: ["get", "list", "create"]
```

### Validación de Certificados SSL/TLS

Para validar certificados SSL/TLS al comunicarse con ONTAP:

```yaml
backend:
  # Los certificados se definen en secret.yaml
  # clientCertificate: <base64>
  # clientPrivateKey: <base64>
  # trustedCACertificate: <base64>
```

**Procedimiento para Generar Certificados**:

1. Generar CSR en el cliente
2. Firmar CSR con CA de ONTAP
3. Codificar certificados en Base64
4. Añadir al secret.yaml

### Mejores Prácticas de Seguridad

1. **No Hardcodear Credenciales**: Nunca incluir username/password en config.yaml.

2. **Usar Secret Manager**: En entornos enterprise, considerar HashiCorp Vault o AWS Secrets Manager.

3. **Limitar Acceso al Namespace**: Restringir quién puede acceder al namespace `trident`.

4. **Monitoreo Continuo**: Implementar alertas para cambios no autorizados en backends.

5. **Backup de Configuración**: Mantener backup seguro de configuraciones críticas.

6. **Documentar Accesos**: Documentar quién tiene acceso a credenciales y configuraciones.

7. **Revisión Periódica**: Auditar permisos y configuraciones periódicamente.

---

## Mejores Prácticas

### Configuración del Backend

#### 1. Nombrado de Recursos

- **Backend Name**: Utilizar nombres descriptivos que identifiquen el entorno y SVM:
```yaml
backend:
  name: prod-san-svm01
```

- **Storage Prefix**: Utilizar prefijos que identifiquen el origen del volumen:
```yaml
backend:
  storagePrefix: k8s-prod
```

#### 2. Límites de Recursos

Configurar límites para prevenir consumo excesivo:

```yaml
backend:
  limitAggregateUsage: "85"        # Máximo 85% de uso del agregado
  limitVolumeSize: "500Gi"         # Volumen máximo de 500GiB
  lunsPerFlexvol: "100"            # Máximo 100 LUNs por FlexVol
```

#### 3. Políticas de Snapshots

Para entornos de producción:

```yaml
defaults:
  snapshotPolicy: daily            # Snapshots diarios
  snapshotReserve: "10"            # 10% reservado para snapshots
```

Para entornos de desarrollo:

```yaml
defaults:
  snapshotPolicy: none             # Sin snapshots automáticos
  snapshotReserve: none            # Sin reserva
```

#### 4. QoS (Quality of Service)

Limitar el rendimiento para workloads específicos:

```yaml
defaults:
  qosPolicy: "bronze-qos"          # Política QoS definida en ONTAP
```

#### 5. Etiquetas (Labels)

Utilizar labels para organización y troubleshooting:

```yaml
backend:
  labels: "environment=production,tier=gold,department=finance"
```

### Configuración de StorageClass

#### 1. StorageClass por Entorno

Crear StorageClasses diferentes para cada entorno:

- **Producción**: Alta disponibilidad y performance
```yaml
storageClass:
  name: ontap-san-prod
  parameters:
    provisioningType: thin
    snapshots: "true"
```

- **Desarrollo**: Configuración más económica
```yaml
storageClass:
  name: ontap-san-dev
  parameters:
    provisioningType: thin
    snapshots: "false"
```

#### 2. Múltiples StorageClasses

Ofrecer diferentes niveles de servicio:

```yaml
# Gold Tier
storageClass:
  name: ontap-san-gold
  parameters:
    backendType: ontap-san
    media: ssd
    snapshots: "true"

---
# Silver Tier  
storageClass:
  name: ontap-san-silver
  parameters:
    backendType: ontap-san
    media: hdd
    snapshots: "true"
```

#### 3. StorageClass por Defecto

Establecer un StorageClass por defecto para simplificar el uso:

```yaml
storageClass:
  isDefault: true
```

**IMPORTANTE**: Solo debe haber un StorageClass marcado como default.

### Operaciones y Mantenimiento

#### 1. Monitoreo

Implementar monitoreo activo de:

- Estado del backend
- Uso de capacidad
- Performance de volúmenes
- Latencia de aprovisionamiento

```bash
# Script de monitoreo simple
while true; do
  kubectl get tbc -n trident
  sleep 300
done
```

#### 2. Backup y Recuperación

Mantener backup de:
- Archivos de configuración (config.yaml)
- Archivos YAML generados
- Documentación de configuración específica del entorno

```bash
# Backup de configuración
tar -czf trident-config-backup-$(date +%Y%m%d).tar.gz \
  config.yaml \
  backend_storage_san.yaml
```

#### 3. Versionado

Utilizar Git para versionar configuraciones:

```bash
# Inicializar repositorio
git init
git add config.yaml *.py requirements.txt README.md
git commit -m "Configuración inicial de Trident SAN"

# Añadir secret.yaml a .gitignore
echo "secret.yaml" >> .gitignore
```

#### 4. Documentación

Mantener documentación actualizada:
- Diagrama de arquitectura de almacenamiento
- Procedimientos de operación estándar
- Contactos de escalación
- Historial de cambios

#### 5. Testing

Probar cambios en entornos no productivos:

```bash
# Crear backend de test
kubectl apply -f backend_storage_san_test.yaml -n trident-test

# Crear PVC de prueba
kubectl apply -f test-pvc.yaml

# Validar aprovisionamiento
kubectl get pvc test-pvc
kubectl get pv

# Cleanup
kubectl delete pvc test-pvc
kubectl delete tbc backend-test -n trident-test
```

### Escalabilidad

#### 1. Múltiples Backends

Para entornos grandes, considerar múltiples backends:

```bash
# Backend para tier gold
python generate_trident_san.py --config config-gold.yaml

# Backend para tier silver
python generate_trident_san.py --config config-silver.yaml
```

#### 2. Auto-escalado

Configurar límites apropiados para permitir crecimiento:

```yaml
backend:
  limitAggregateUsage: "85"        # Dejar 15% para crecimiento
  limitVolumeSize: "1Ti"           # Permitir volúmenes grandes si es necesario
```

---

## Resolución de Problemas

### Metodología de Troubleshooting

1. **Identificar el Síntoma**: Qué está fallando exactamente
2. **Recopilar Información**: Logs, eventos, estado de recursos
3. **Aislar la Causa**: Determinar el componente problemático
4. **Aplicar Solución**: Corregir el problema
5. **Verificar**: Confirmar que el problema se resolvió
6. **Documentar**: Registrar el problema y la solución

### Herramientas de Diagnóstico

#### Script de Diagnóstico Básico

```bash
#!/bin/bash
# diagnose-trident.sh

echo "=== Estado de Trident ==="
kubectl get pods -n trident

echo -e "\n=== Backends Configurados ==="
kubectl get tbc -n trident

echo -e "\n=== StorageClasses ==="
kubectl get sc

echo -e "\n=== PVCs Pendientes ==="
kubectl get pvc --all-namespaces | grep Pending

echo -e "\n=== Eventos Recientes ==="
kubectl get events -n trident --sort-by='.lastTimestamp' | tail -20
```

#### Comandos Útiles

```bash
# Ver logs de todos los pods de Trident
kubectl logs -n trident -l app=trident-csi --all-containers=true --tail=100

# Verificar conectividad a ONTAP desde un nodo
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- bash

# Verificar configuración del backend
kubectl get tbc backend-jc-san -n trident -o yaml

# Ver detalles de un PVC problemático
kubectl describe pvc <pvc-name> -n <namespace>
```

### Problemas Comunes y Soluciones

#### Problema: Backend No Se Conecta a ONTAP

**Diagnóstico:**
```bash
kubectl describe tbc <backend-name> -n trident
# Buscar en Events: connection refused, timeout, etc.
```

**Posibles Causas:**
1. Firewall bloqueando puerto 443
2. Management LIF incorrecta
3. Credenciales inválidas
4. SVM detenida o no existe

**Solución:**
```bash
# Probar conectividad desde un pod
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl -k https://<managementLIF>

# Verificar credenciales
kubectl get secret trident-creds -n trident -o jsonpath='{.data.username}' | base64 -d

# Verificar SVM en ONTAP
# (desde ONTAP CLI)
vserver show -vserver <svm-name>
```

#### Problema: Aprovisionamiento Lento

**Diagnóstico:**
```bash
# Ver tiempo de aprovisionamiento
kubectl describe pvc <pvc-name> | grep "successfully provisioned"

# Ver logs de Trident
kubectl logs -n trident -l app=trident-csi --tail=200 | grep <pvc-name>
```

**Posibles Causas:**
1. ONTAP sobrecargado
2. Agregado sin espacio suficiente
3. Latencia de red alta

**Solución:**
```bash
# Verificar performance de ONTAP
# (desde ONTAP CLI)
statistics show -object aggregate -instance <aggregate-name>

# Verificar latencia de red
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- \
  ping -c 10 <managementLIF>
```

#### Problema: PVC en Pending Indefinidamente

**Diagnóstico:**
```bash
kubectl describe pvc <pvc-name>
# Ver sección Events
```

**Checklist:**
- [ ] Backend está en estado Bound
- [ ] StorageClass existe y es correcta
- [ ] Hay capacidad disponible en el agregado
- [ ] Los selectores del PVC coinciden con el backend

---

## Referencias y Documentación

### Documentación Oficial de NetApp

- **NetApp Trident Documentation**: [https://docs.netapp.com/us-en/trident/](https://docs.netapp.com/us-en/trident/)
- **ONTAP SAN Configuration Guide**: [https://docs.netapp.com/ontap-9/index.jsp](https://docs.netapp.com/ontap-9/index.jsp)
- **Trident GitHub Repository**: [https://github.com/NetApp/trident](https://github.com/NetApp/trident)

### Documentación de Kubernetes

- **Kubernetes Storage Documentation**: [https://kubernetes.io/docs/concepts/storage/](https://kubernetes.io/docs/concepts/storage/)
- **Persistent Volumes**: [https://kubernetes.io/docs/concepts/storage/persistent-volumes/](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- **Storage Classes**: [https://kubernetes.io/docs/concepts/storage/storage-classes/](https://kubernetes.io/docs/concepts/storage/storage-classes/)

### Estándares y Especificaciones

- **Container Storage Interface (CSI) Specification**: [https://github.com/container-storage-interface/spec](https://github.com/container-storage-interface/spec)
- **iSCSI Protocol**: RFC 3720
- **CHAP Authentication**: RFC 1994

### Comunidad y Soporte

- **NetApp Community Forums**: [https://community.netapp.com/](https://community.netapp.com/)
- **Kubernetes Slack**: #sig-storage channel
- **NetApp Slack**: #trident channel

### Comandos de Referencia Rápida

```bash
# Verificar versiones
python --version
kubectl version --short
kubectl get pods -n trident -l app=trident-csi -o jsonpath='{.items[0].spec.containers[0].image}'

# Generar configuración
python generate_trident_san.py

# Desplegar backend
kubectl create secret generic trident-creds --from-literal=username=vsadmin --from-literal=password=pass -n trident
kubectl apply -f backend_storage_san.yaml -n trident

# Verificar estado
kubectl get tbc -n trident
kubectl get sc
kubectl describe tbc <backend-name> -n trident

# Troubleshooting
kubectl logs -n trident -l app=trident-csi --tail=100
kubectl get events -n trident --sort-by='.lastTimestamp'
```

---

## Contacto y Soporte

Para soporte técnico, consultas o reportar problemas:

- **Documentación NetApp**: [https://docs.netapp.com](https://docs.netapp.com)
- **Documentación Parametrización RHOSO**: Consultar PDF de Parametrización RHOSO
- **Soporte NetApp**: Contactar con su Partner o Representante de NetApp

---

## Historial de Cambios

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 2.0 | Marzo 2026 | - Actualización completa de documentación<br>- Añadido soporte para campos configurables del backend<br>- Implementación de gestión de credenciales en Secret<br>- Mejoras en validación y manejo de errores<br>- Actualización de valores por defecto (snapshotReserve: none)<br>- Documentación extendida de seguridad |
| 1.0 | Febrero 2026 | Versión inicial del generador |

---

**Última actualización:** Marzo 2026  
**Versión del generador:** 2.0  
**Autor:** Professional Services NetApp

---
