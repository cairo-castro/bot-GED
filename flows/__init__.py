"""
Módulo de fluxos para diferentes tipos de documentos médicos
"""

from .base_flow import BaseFlow
from .atestados import AtestadosFlow
from .prontuarios import ProntuariosFlow
from .exames import ExamesFlow

__all__ = ['BaseFlow', 'AtestadosFlow', 'ProntuariosFlow', 'ExamesFlow']