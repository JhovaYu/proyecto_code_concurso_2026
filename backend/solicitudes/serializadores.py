"""Contratos DRF para solicitudes; todavía no están conectados a rutas."""

from collections.abc import Mapping

from rest_framework import serializers


class EntradaEstricta(serializers.Serializer):
    """Rechaza campos ajenos al contrato, incluidos datos de autorización."""

    def to_internal_value(self, data):
        if isinstance(data, Mapping):
            desconocidos = set(data) - set(self.fields)
            if desconocidos:
                raise serializers.ValidationError(
                    {campo: ["Campo no permitido."] for campo in sorted(desconocidos)}
                )
        return super().to_internal_value(data)


class TextoEstricto(serializers.CharField):
    """Evita convertir números u otros tipos a texto automáticamente."""

    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail("invalid")
        return super().to_internal_value(data)


class EnteroEstricto(serializers.IntegerField):
    """Acepta enteros, excluyendo booleanos y números decimales."""

    def to_internal_value(self, data):
        if isinstance(data, bool) or not isinstance(data, int):
            self.fail("invalid")
        return super().to_internal_value(data)


class DatosBorradorSerializer(EntradaEstricta):
    # El borrador admite datos incompletos; el dominio valida antes de enviarlo.
    titulo = TextoEstricto(required=False, allow_blank=True, default="")
    descripcion = TextoEstricto(required=False, allow_blank=True, default="")
    categoria = TextoEstricto(required=False, allow_blank=True, default="")
    poblacion_estimada = EnteroEstricto(required=False, allow_null=True, default=None)


class CrearSolicitudSerializer(DatosBorradorSerializer):
    comunidad = TextoEstricto(allow_blank=False)


class MensajeSerializer(EntradaEstricta):
    mensaje = TextoEstricto(allow_blank=False, trim_whitespace=True)


class BooleanoEstricto(serializers.BooleanField):
    def to_internal_value(self, data):
        if not isinstance(data, bool):
            self.fail("invalid", input=data)
        return data


class ResolucionSerializer(EntradaEstricta):
    aprobar = BooleanoEstricto()
    justificacion = TextoEstricto(allow_blank=False, trim_whitespace=True)


class SolicitudSerializer(serializers.Serializer):
    """Representación de la solicitud en memoria, sin identificador persistente."""

    comunidad = serializers.CharField(read_only=True)
    titulo = serializers.CharField(source="datos.titulo", read_only=True)
    descripcion = serializers.CharField(source="datos.descripcion", read_only=True)
    categoria = serializers.CharField(source="datos.categoria", read_only=True)
    poblacion_estimada = serializers.IntegerField(source="datos.poblacion_estimada", read_only=True, allow_null=True)
    estado = serializers.CharField(source="estado.value", read_only=True)
    mensaje_ong = serializers.CharField(read_only=True)
    respuesta_representante = serializers.CharField(read_only=True)
    justificacion = serializers.CharField(read_only=True)
