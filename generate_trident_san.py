#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          GENERADOR OPTIMIZADO DE CONFIGURACIÓN TRIDENT SAN                   ║
║                    para OpenShift / Kubernetes                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

DESCRIPCIÓN:
    Generador Python moderno y optimizado para crear configuraciones YAML de
    NetApp Trident SAN. Utiliza dataclasses, validación automática y arquitectura
    modular para generar configuraciones seguras y estandarizadas.

ARCHIVOS GENERADOS:
    - backend_storage_san.yaml: TridentBackendConfig + StorageClass de Kubernetes
    - secret.yaml: Secret con credenciales de acceso a NetApp ONTAP

USO:
    python generate_trident_san.py

CONFIGURACIÓN:
    Edita config.yaml con tus valores. Mínimo requerido:
    
    backend:
      managementLIF: IP_DE_GESTION
      dataLIF: IP_DE_DATOS
      svm: NOMBRE_DEL_SVM
    
    storageClass:
      name: NOMBRE_STORAGE_CLASS

AUTOR: PS NetApp
VERSION: 2.0 (Optimizada)
"""

import yaml
import re
import os
from typing import Dict, Any
from dataclasses import dataclass, asdict, field


# ══════════════════════════════════════════════════════════════════════════════
#                         CONFIGURACIÓN CENTRALIZADA
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class BackendDefaults:
    """
    Valores por defecto aplicados a todos los volúmenes aprovisionados.
    
    Estos valores se usan cuando se crea un nuevo Volume a través
    del StorageClass. Optimizados para seguridad y eficiencia.
    
    """
    spaceReserve: str = 'none'
    spaceAllocation: str = 'true'
    snapshotPolicy: str = 'none'
    snapshotReserve: str = 'none'
    encryption: str = 'false'
    qosPolicy: str = ''
    adaptiveQosPolicy: str = ''
    tieringPolicy: str = 'none'
    luksEncryption: str = ''
    nameTemplate: str = ''


@dataclass
class DebugTraceFlags:
    """
    Indicadores de depuración para usar al solucionar problemas.
    
    ADVERTENCIA: No usar debugTraceFlags a menos que esté solucionando problemas 
    y necesite un registro detallado.
    
    Args:
        api: Traza llamadas a la API de ONTAP desde el pod de Trident
        method: Traza métodos internos de Trident
    """
    api: bool = False
    method: bool = False


@dataclass
class BackendConfig:
    """
    Configuración completa del TridentBackendConfig.
    
    Define cómo Trident se conecta al storage de NetApp ONTAP SAN.
    
    Campos obligatorios:
        - managementLIF: IP de gestión del SVM
        - dataLIF: IP de datos para conexiones iSCSI
        - svm: Storage Virtual Machine en ONTAP

    """
    name: str = 'backend-jc-san'
    namespace: str = 'trident'
    version: int = 1
    backendName: str = ''  # Si está vacío, se genera automáticamente como ontap-san_{dataLIF}
    storageDriverName: str = 'ontap-san'
    useREST: bool = True
    managementLIF: str = ''  # Campo obligatorio - debe especificarse en config.yaml
    dataLIF: str = ''  # Campo obligatorio - debe especificarse en config.yaml
    svm: str = ''  # Campo obligatorio - debe especificarse en config.yaml
    storagePrefix: str = 'trident'
    credentialsName: str = 'trident-creds'  # Nombre del secret de credenciales
    labels: str = ''
    clientCertificate: str = ''
    clientPrivateKey: str = ''
    trustedCACertificate: str = ''
    aggregate: str = ''
    limitAggregateUsage: str = ''
    limitVolumeSize: str = ''
    lunsPerFlexvol: str = '100'
    sanType: str = 'fcp'
    formatOptions: str = ''
    limitVolumePoolSize: str = ''
    denyNewVolumePools: str = 'false'
    debugTraceFlags: DebugTraceFlags = field(default_factory=DebugTraceFlags)
    defaults: BackendDefaults = field(default_factory=BackendDefaults)


@dataclass
class StorageClassParameters:
    """
    Parámetros de selección de backend para el StorageClass.
    
    Args:
        backendType: Tipo de driver de Trident (ontap-san)
        fsType: Sistema de archivos (ext4, xfs)
        provisioningType: Thin o thick provisioning
        snapshots: Soporte de snapshots de Kubernetes
    """
    backendType: str = 'ontap-san'
    fsType: str = 'ext4'
    provisioningType: str = 'thin'
    snapshots: str = 'true'


@dataclass
class StorageClassConfig:
    """
    Configuración del StorageClass de Kubernetes.
    
    Args:
        name: Nombre visible del StorageClass en K8s
        isDefault: Si es true, se usa cuando no se especifica StorageClass en PVC
        syncWave: Orden de sincronización para ArgoCD (deployment automatizado)
        provisioner: Driver CSI de Trident (default: csi.trident.netapp.io)
        reclaimPolicy: Política de eliminación de volúmenes (Delete/Retain)
        allowVolumeExpansion: Permitir expansión de volúmenes dinámicamente
        volumeBindingMode: Modo de binding (Immediate/WaitForFirstConsumer)
        parameters: Criterios de selección de backend
    """
    name: str = 'rhoso-san'
    isDefault: bool = True
    syncWave: str = '5'
    provisioner: str = 'csi.trident.netapp.io'
    reclaimPolicy: str = 'Delete'
    allowVolumeExpansion: bool = True
    volumeBindingMode: str = 'Immediate'
    parameters: StorageClassParameters = field(default_factory=StorageClassParameters)


@dataclass
class SecretConfig:
    """
    Credenciales de acceso al backend NetApp ONTAP.
    
    IMPORTANTE: Con TridentBackendConfig, el Secret contiene las credenciales
    del SVM (username/password) y los campos de certificados (si se usa 
    autenticación por certificados).
    
    En versiones recientes de Trident, los campos de certificados son 
    "forbidden attributes" en el backend spec y DEBEN ir en el Secret.
    
    El backend referencia el Secret mediante credentials.name.
    
    Este dataclass es OPCIONAL - solo se usa si quieres que el script genere
    el archivo secret.yaml automáticamente. En producción, es común crear y 
    gestionar secret.yaml manualmente.
    
    Args:
        name: Nombre del Secret en Kubernetes (default: trident-creds)
        username: Usuario del SVM - OPCIONAL (solo para generar secret.yaml)
        password: Contraseña del usuario - OPCIONAL (solo para generar secret.yaml)
    
    Campos que se agregan automáticamente al secret desde backend config:
        - clientCertificate, clientPrivateKey, trustedCACertificate (si se definen)
    """
    name: str = 'trident-creds'
    username: str = ''  # Opcional - solo para generación automática de secret.yaml
    password: str = ''  # Opcional - solo para generación automática de secret.yaml


@dataclass
class TridentConfig:
    """
    Configuración completa de Trident SAN - Contenedor principal.
    
    Agrupa todas las configuraciones necesarias para desplegar
    un backend de Trident SAN funcional en OpenShift/Kubernetes.
    
    Componentes:
        - backend: Cómo conectarse al storage NetApp
        - storageClass: Cómo los usuarios solicitan almacenamiento
        - secret: Credenciales de acceso
    """
    backend: BackendConfig = field(default_factory=BackendConfig)
    storageClass: StorageClassConfig = field(default_factory=StorageClassConfig)
    secret: SecretConfig = field(default_factory=SecretConfig)


# ══════════════════════════════════════════════════════════════════════════════
#                          FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════════════════════

def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusiona dos diccionarios recursivamente de forma inteligente.
    
    Los valores del usuario (override) reemplazan los valores por defecto (base).
    Cuando ambos contienen diccionarios anidados, se combinan recursivamente.
    
    Args:
        base: Diccionario con valores por defecto
        override: Diccionario con valores del usuario (config.yaml)
    
    Returns:
        Diccionario fusionado con valores de override prevaleciendo
    
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config_file: str = "config.yaml") -> TridentConfig:
    """
    Carga y valida la configuración desde un archivo YAML.
    
    Proceso:
        1. Lee el archivo config.yaml del usuario
        2. Fusiona con valores por defecto
        3. Reconstruye objetos dataclass con validación de tipos
        4. Valida campos obligatorios (managementLIF, dataLIF, svm)
        5. Maneja compatibilidad de formatos (credentials anidado vs simple)
    
    Args:
        config_file: Ruta al archivo YAML de configuración
    
    Returns:
        TridentConfig completo y validado listo para generar YAMLs
    
    Raises:
        ValueError: Si falta algún campo obligatorio
        FileNotFoundError: Si config_file no existe
    
    """
    if not os.path.exists(config_file):
        return TridentConfig()
    
    with open(config_file, 'r', encoding='utf-8') as f:
        user_config = yaml.safe_load(f) or {}
    
    # Crear configuración por defecto
    default_config = TridentConfig()
    
    # Convertir a diccionario y fusionar
    default_dict = asdict(default_config)
    merged = merge_dicts(default_dict, user_config)
    
    # Reconstruir objetos anidados desde diccionario fusionado
    backend_defaults = BackendDefaults(**merged.get('backend', {}).get('defaults', {}))
    debug_trace_flags = DebugTraceFlags(**merged.get('backend', {}).get('debugTraceFlags', {}))
    backend_data = {
        **merged.get('backend', {}),
        'defaults': backend_defaults,
        'debugTraceFlags': debug_trace_flags
    }
    
    # ===== COMPATIBILIDAD: Manejar credentials.name anidado =====
    # Extraer credentials.name antes de crear BackendConfig
    backend_config_dict = merged.get('backend', {})
    if 'credentials' in backend_config_dict and isinstance(backend_config_dict['credentials'], dict):
        credentials_name = backend_config_dict['credentials'].get('name', 'trident-creds')
        backend_data['credentialsName'] = credentials_name
    
    # Quitar 'credentials' del backend_data para que no cause error en BackendConfig
    backend_data.pop('credentials', None)
    
    storage_class_params = StorageClassParameters(**merged.get('storageClass', {}).get('parameters', {}))
    storage_class_data = {**merged.get('storageClass', {}), 'parameters': storage_class_params}
    
    backend_config = BackendConfig(**backend_data)
    
    # Si hay secret.name definido, usarlo (tiene prioridad)
    secret_data = merged.get('secret', {})
    if not secret_data.get('name'):
        secret_data['name'] = backend_config.credentialsName
    
    # ===== VALIDACIONES DE CAMPOS OBLIGATORIOS =====
    
    secret_config = SecretConfig(**secret_data)
    
    errors = []
    if not backend_config.managementLIF:
        errors.append("  - backend.managementLIF")
    if not backend_config.dataLIF:
        errors.append("  - backend.dataLIF")
    if not backend_config.svm:
        errors.append("  - backend.svm")
    if not backend_config.credentialsName:
        errors.append("  - backend.credentials.name")
    
    if errors:
        raise ValueError(
            "ERROR: Los siguientes campos son obligatorios en config.yaml:\n" +
            "\n".join(errors)
        )
    
    return TridentConfig(
        backend=backend_config,
        storageClass=StorageClassConfig(**storage_class_data),
        secret=secret_config
    )


def comment_empty_fields(filepath: str) -> None:
    """
    Comenta automáticamente líneas con valores vacíos en YAML generado.
    
    Esta función mejora la legibilidad del YAML manteniendo visible la
    documentación de parámetros opcionales sin afectar el funcionamiento.
    
    Comportamiento:
        - NO comenta campos contenedores (metadata, spec, defaults, etc.)
        - SÍ comenta líneas con valores explícitamente vacíos ('', "")
        - Preserva indentación original
    
    Args:
        filepath: Ruta del archivo YAML a procesar
    
    """
    # Campos que son contenedores y nunca deben ser comentados
    container_fields = {
        'metadata', 'annotations', 'parameters', 'credentials', 
        'debugTraceFlags', 'spec', 'defaults', 'data', 'stringData'
    }
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.splitlines(keepends=True)
    modified = []
    
    for line in lines:
        # Extraer el nombre del campo si existe
        field_match = re.match(r"^\s*(\w+):\s*(.*)$", line)
        
        if field_match:
            field_name = field_match.group(1)
            field_value = field_match.group(2).strip()
            
            # NO comentar si:
            # 1. Es un campo contenedor
            # 2. No tiene valor (es un objeto anidado)
            # 3. Tiene un valor no vacío
            if field_name in container_fields or not field_value or \
               (field_value and field_value not in ["''", '""', "''", '""']):
                modified.append(line)
            else:
                # Comentar solo valores explícitamente vacíos ('', "")
                if field_value in ["''", '""', "''", '""']:
                    modified.append(re.sub(r'^(\s*)', r'\1# ', line))
                else:
                    modified.append(line)
        else:
            modified.append(line)
    
    # Escribir una sola vez
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(modified)


# ══════════════════════════════════════════════════════════════════════════════
#                      GENERADORES DE RECURSOS YAML
# ══════════════════════════════════════════════════════════════════════════════

def create_backend_yaml(config: BackendConfig, secret_name: str) -> Dict[str, Any]:
    """
    Genera la estructura YAML del TridentBackendConfig.
    
    Transforma la configuración de Python en un diccionario que representa
    el recurso Kubernetes TridentBackendConfig. Incluye lógica especial:
    
    - Auto-generación de backendName basado en dataLIF sanitizada (si no se especifica)
    - Uso de campos configurables (storageDriverName, sanType, useREST, etc.)
    - Inclusión de defaults y debugTraceFlags como subsecciones
    
    Args:
        config: Configuración del backend validada
        secret_name: Nombre del Secret de Kubernetes con credenciales
    
    Returns:
        Dict representando TridentBackendConfig listo para serializar a YAML

    """
    backend = asdict(config)
    defaults = backend.pop('defaults')
    debug_trace_flags = backend.pop('debugTraceFlags')
    credentials_name = backend.pop('credentialsName')  # No incluir en el spec
    backend_name = backend.pop('name')  # Extraer name para metadata, no debe estar en spec
    namespace = backend.pop('namespace')  # Extraer namespace para metadata
    version = backend.pop('version')  # Extraer version para spec
    backend_name_spec = backend.pop('backendName')  # Extraer backendName para spec
    storage_driver_name = backend.pop('storageDriverName')  # Extraer storageDriverName
    use_rest = backend.pop('useREST')  # Extraer useREST
    
    # Remover campos de certificados (son forbidden attributes en el backend spec)
    backend.pop('clientCertificate', None)
    backend.pop('clientPrivateKey', None)
    backend.pop('trustedCACertificate', None)
    
    # Generar backendName automáticamente solo si no se especificó: ontap-san_<dataLIF>
    # Reemplazar puntos por guiones bajos para nombres válidos
    if not backend_name_spec:
        data_lif_sanitized = backend['dataLIF'].replace('.', '_')
        backend_name_spec = f"{storage_driver_name}_{data_lif_sanitized}"
    
    return {
        'apiVersion': 'trident.netapp.io/v1',
        'kind': 'TridentBackendConfig',
        'metadata': {
            'name': backend_name,
            'namespace': namespace
        },
        'spec': {
            'version': version,
            'backendName': backend_name_spec,
            'storageDriverName': storage_driver_name,
            'useREST': use_rest,
            **backend,
            'defaults': defaults,
            'debugTraceFlags': debug_trace_flags,
            'credentials': {'name': secret_name}
        }
    }


def create_storage_class_yaml(config: StorageClassConfig) -> Dict[str, Any]:
    """
    Genera la estructura YAML del StorageClass de Kubernetes.
    
    Args:
        config: Configuración del StorageClass validada
    
    Returns:
        Dict representando StorageClass listo para serializar a YAML
    
    """
    return {
        'apiVersion': 'storage.k8s.io/v1',
        'kind': 'StorageClass',
        'metadata': {
            'name': config.name,
            'annotations': {
                'storageclass.kubernetes.io/is-default-class': str(config.isDefault).lower(),
                'argocd.argoproj.io/sync-wave': config.syncWave
            }
        },
        'provisioner': config.provisioner,
        'reclaimPolicy': config.reclaimPolicy,
        'parameters': asdict(config.parameters),
        'allowVolumeExpansion': config.allowVolumeExpansion,
        'volumeBindingMode': config.volumeBindingMode
    }


def create_secret_yaml(config: SecretConfig, backend_config: BackendConfig = None) -> Dict[str, Any]:
    """
    Genera la estructura YAML del Secret con credenciales de NetApp.
    
    Crea un Secret Opaque de Kubernetes que almacena las credenciales
    que Trident usa para autenticarse contra el SVM de NetApp ONTAP.
    
    Args:
        config: Configuración del Secret validada
        backend_config: Configuración del backend (opcional, para incluir certificados)
    
    Returns:
        Dict representando Secret listo para serializar a YAML
    """
    secret_data = {
        'username': config.username,
        'password': config.password
    }
    
    # Si se usan certificados, agregarlos al secret (son forbidden attributes)
    if backend_config:
        if backend_config.clientCertificate:
            secret_data['clientCertificate'] = backend_config.clientCertificate
        if backend_config.clientPrivateKey:
            secret_data['clientPrivateKey'] = backend_config.clientPrivateKey
        if backend_config.trustedCACertificate:
            secret_data['trustedCACertificate'] = backend_config.trustedCACertificate
    
    return {
        'apiVersion': 'v1',
        'kind': 'Secret',
        'metadata': {'name': config.name},
        'type': 'Opaque',
        'stringData': secret_data
    }


# ══════════════════════════════════════════════════════════════════════════════
#                          FUNCIÓN PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def generate_trident_files(
    config: TridentConfig,
    backend_file: str = "backend_storage_san.yaml",
    secret_file: str = "secret.yaml"
) -> None:
    """
    Orquesta la generación completa de archivos YAML para Trident SAN.
    
    Flujo de ejecución:
        1. Genera diccionario de TridentBackendConfig
        2. Genera diccionario de StorageClass
        3. Genera diccionario de Secret
        4. Serializa backend + StorageClass a backend_storage_san.yaml
        5. Comenta campos vacíos en backend_storage_san.yaml 
        6. Serializa Secret a secret.yaml
        7. Muestra confirmación
    
    Args:
        config: Configuración completa validada y fusionada con defaults
        backend_file: Nombre/ruta del archivo de backend (default: backend_storage_san.yaml)
        secret_file: Nombre/ruta del archivo de secret (default: secret.yaml)
    
    Archivos generados:
        backend_storage_san.yaml: Contiene 2 recursos separados por '---':
            - TridentBackendConfig (cómo conectarse a NetApp)
            - StorageClass (cómo usuarios solicitan storage)
        
        secret.yaml: Contiene 1 recurso:
            - Secret (credenciales de acceso)
    
    Nota:
        Los archivos se sobrescriben si ya existen.
    """

    # Generar recursos
    backend = create_backend_yaml(config.backend, config.secret.name)
    storage_class = create_storage_class_yaml(config.storageClass)
    secret = create_secret_yaml(config.secret, config.backend)
    
    # Escribir backend y storage class
    with open(backend_file, 'w', encoding='utf-8') as f:
        yaml.dump(backend, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        f.write('\n---\n\n')
        yaml.dump(storage_class, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Comentar campos vacíos
    comment_empty_fields(backend_file)
    print(f"Archivo generado: {backend_file}")

def main(config_file: str = None) -> None:
    """
    Punto de entrada principal del script.
    
    Orquesta todo el proceso de generación:
        1. Busca config.yaml en el directorio actual
        2. Carga y valida la configuración
        3. Genera los archivos YAML de salida
        4. Muestra instrucciones para el usuario
    
    Args:
        config_file: Ruta del archivo de configuración (default: config.yaml)
                    Si es None, busca automáticamente config.yaml
    
    Returns:
        None. Genera archivos y muestra output en consola.
    
    Salida en consola:
        - Confirmación del archivo de config usado
        - Confirmación de archivos generados
        - Instrucciones para personalizar
    
    Raises:
        FileNotFoundError: Si config.yaml no existe
        ValueError: Si faltan campos obligatorios en config.yaml
    """
    # Si no se especifica archivo, usar config.yaml
    if config_file is None:
        config_file = 'config.yaml'
        
        if not os.path.exists(config_file):
            print("ERROR: No se encontró el archivo de configuración.")
            print("\nCrea el archivo:")
            print("  - config.yaml")
            return
    
    print(f"Usando configuración: {config_file}")
    
    config = load_config(config_file)
    generate_trident_files(config)
    
    print(f"\n ------------------------------------------------------------------")
    print(f"\n Instrucciones:")
    print(f"  1. Edita config.yaml y secret.yaml")
    print(f"  2. Ejecuta: python generate_trident_nas.py")
    print(f"  3. Aplica los archivos generados en tu clúster:")
    print(f"     - kubectl apply -f secret.yaml -n trident")
    print(f"     - kubectl apply -f backend_storage_san.yaml -n trident")
    print(f"  4. Verifica los recursos creados:")
    print(f"     - kubectl get tridentbackendconfig -n trident")
    print(f"\n ------------------------------------------------------------------")


if __name__ == "__main__":
    main()
