from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import Http404, IsAuthenticated


from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import transaction

from .serializer import LoginSerializer, UserSerializer, ChangePasswordSerializer


# Create your views here.
@api_view(["POST"])
def register(request):
    serializer = UserSerializer(data=request.data)
    # s convierte la data dada por el servidor en un json
    if serializer.is_valid():
        try:
            with transaction.atomic():  # pyright: ignore
                # se pregunta si el serializador es valido
                serializer.save()
                # si es valido se guarda

                user = User.objects.get(username=serializer.data["username"])  # pyright: ignore
                # Se crea un objeto tipo "usuario"
                user.set_password(serializer.data["password"])  # pyright: ignore
                user.save()
                token = Token.objects.create(user=user)  # pyright: ignore
                staff = user.is_staff
                # ahora se crea un token en la base de datos que esta relacionado con el usuario recien creado
                return Response(
                    {
                        "token": token.key,
                        "user": serializer.data["username"],  # pyright: ignore
                        "email": serializer.data["email"],  # pyright: ignore
                        "staff": staff,
                    },
                    status=status.HTTP_201_CREATED,
                )
                # se debuelve tanto el la key del token como los datos del usuario y por ultimo el status creado

        except Exception:
            return Response(
                {"error": "An error occurred while creating the user."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    # si el serializer no devuelve un error


@api_view(["POST"])
def login(request):
    data = LoginSerializer(data=request.data)

    if data.is_valid():
        try:
            user = get_object_or_404(User, username=data.data["username"])  # pyright: ignore
            # se rpegunta si existe el usuario
            if not user.check_password(data.data["password"]):  # pyright: ignore
                return Response(
                    {"Error": "Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST
                )
                # Se pregunta si la contrasaña esta correcta y si no es asi se manda error
            serializer = UserSerializer(instance=user)
            # Se crea un instancia del serializer
            token, created = Token.objects.get_or_create(user=user)  # pyright: ignore
            # se obtienen el token del usuario
            staff = user.is_staff

            return Response(
                {"user": serializer.data, "token": token.key, "staff": staff},
                status=status.HTTP_200_OK,
            )
            # se devuelve el token del usuario y los datos del usuario
        except Http404:
            return Response(
                {"error": "user not exist"}, status=status.HTTP_400_BAD_REQUEST
            )

    return Response({"error": data.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes({IsAuthenticated})
# se pide el token de autorizacion y si el usuario esta autenticado
def log(request):
    print(request.user.password)
    return Response({"nice": "Perfecto"}, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    # se serializa el los datos en un json
    print(serializer.is_valid())
    if serializer.is_valid():
        # se regunta si el usuario es valido y si es valido se guarda en la base de datos
        serializer.save()
        return Response({"User": serializer.data}, status=status.HTTP_200_OK)

    return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete(request):
    user = request.user
    # se obtiene el nombre de usuario del user
    try:
        user = User.objects.get(username=user.username)
        # si el usuario existe los datos se guardan el la variable
    except User.DoesNotExist:  # pyright: ignore
        return Response({"Error": "User dont exist"}, status=status.HTTP_404_NOT_FOUND)
        # si no existe el personaje devuelve un error

    user.delete()
    # si existe se elimina el usuario
    return Response({"success": "success"}, status=status.HTTP_200_OK)
    # y se devuelve el exito


@api_view(["GET"])
def validate_user(request):
    try:
        key = request.data.get("token")
        key = Token.objects.get(key=key)  # pyright: ignore

        return Response({"reponse": key.user_id}, status=status.HTTP_200_OK)
    except:
        return Response({"reponse": "not valid"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def validate_staff(request):
    try:
        key = request.data.get("token") or request.data.get("Token")
        key = Token.objects.get(key=key)  # pyright: ignore
        user = User.objects.get(id=key.user_id)
        if user.is_staff:
            return Response({"reponse": key.user_id}, status=status.HTTP_200_OK)
        return Response({"response": "not valid"}, status=status.HTTP_400_BAD_REQUEST)
    except Token.DoesNotExist:  # pyright: ignore
        return Response({"Error": "it's not staff"}, status=status.HTTP_404_NOT_FOUND)
    except:
        return Response({"response": "not valid"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def make_staff(request):
    user = request.user
    try:
        user = User.objects.get(username=user.username)
        user.is_staff = True
    except User.DoesNotExist:  # pyright: ignore
        return Response({"Error": "User dont exist"}, status=status.HTTP_404_NOT_FOUND)

    user.save()
    return Response({"success": "success"}, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@authentication_classes([TokenAuthentication])
@permission_classes({IsAuthenticated})
def change_password(request):
    try:
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(
                User,
                username=serializer.validated_data["username"],  # pyright: ignore
            )
            # se rpegunta si existe el usuario
            if not user.check_password(serializer.validated_data["password"]):  # pyright: ignore
                return Response(
                    {"Error": "Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(serializer.validated_data["new_password"])  # pyright: ignore
            user.save()

            return Response({"Check": "Password changed"}, status=status.HTTP_200_OK)
        else:
            print("prueba")
            return Response(
                {"Error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
    except User.DoesNotExist:  # pyright: ignore
        return Response({"Error": "User dont exist"}, status=status.HTTP_404_NOT_FOUND)
