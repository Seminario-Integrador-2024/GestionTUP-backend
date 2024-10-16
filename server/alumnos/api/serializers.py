#  third party imports

from rest_framework import serializers

from server.alumnos.models import Alumno

#  custom imports
from server.alumnos.models import Inhabilitacion, AlumnosAInhabilitar
from server.materias.models import Materia
from server.users.api.serializers import UserCreateSerializer
from server.users.models import User


class AlumnoRetrieveSerializer(serializers.ModelSerializer):
    alumno_link = serializers.SerializerMethodField()
    dni = serializers.IntegerField(source="user.dni", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    
    class Meta:
        model = Alumno
        # fields = "__all__"
        exclude = ["user"]
        lookup_field = "dni"

    def get_alumno_link(self, obj):
        request = self.context.get("request")
        if request is not None:
            base_url = request.build_absolute_uri("/")
            if obj.user.dni:
                return f"{base_url}alumnos/{obj.user.dni}/"
        return None


class AlumnoCreateSerializer(serializers.ModelSerializer[Alumno]):
    user = UserCreateSerializer(required=True, many=False, allow_null=False)

    class Meta:
        model = Alumno
        fields = "__all__"

    def create(self, validated_data) -> Alumno:
        user_data = validated_data.pop("user")
        # create user instance
        user_instance = User.objects.create_user(**user_data)
        user_instance.set_password(user_data.get("password"))
        user_instance.save()
        # create alumno instance and link it to user
        return Alumno.objects.create(user=user_instance, **validated_data)


class AlumnosPagYNoCuotaSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Alumno
        fields = ["user", "full_name", "estado_financiero", "legajo"]



class AlumnosInhabilitadosSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    fecha_inhabilitacion = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Alumno
        fields = ["user", "full_name", "estado_financiero", "legajo", "fecha_inhabilitacion"]

    def get_fecha_inhabilitacion(self, obj):
        # Obtener la última inhabilitación del alumno, si existe
        ultima_inhabilitacion = Inhabilitacion.objects.filter(id_alumno=obj).order_by('-fecha_desde').last()
        if ultima_inhabilitacion:
            print(ultima_inhabilitacion)
            return ultima_inhabilitacion.fecha_desde
        return None

class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = "__all__"

class AlumnosAInhabilitarSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumnosAInhabilitar
        fields = "__all__"


class InhabilitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inhabilitacion
        fields = '__all__'