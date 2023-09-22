import streamlit as st
import pandas as pd
from github import Github
import io
import github

def hide_password_input(input_label):
    password = st.text_input(input_label, type="password", key=input_label)
    return password

# Función para verificar la contraseña ingresada
def verificar_contraseña(contraseña):
    if contraseña == st.secrets["CONTRASEÑA"]:
        return True
    else:
        return False


st.write("---")

colA, colB, colC = st.columns(3)
with colA :
    st.image("imgs/CAME-Transparente.png", use_column_width=True, width=600)
# Imagen común a todas las páginas ya que esta por fuera de las funciones
with colB : 
    contraseña = hide_password_input("Ingrese la contraseña:")
    
with colC :
    st.write("")    

st.write("---")

# Verificar la contraseña
if verificar_contraseña(contraseña) == True:
    st.success("Contraseña válida. Acceso concedido.")
    # Establecer el estado de autenticación de la sesión
    st.session_state.autenticado = True
    # Creamos la conexión
else:
    st.error('Contraseña no válida.')    

if not st.session_state.get('autenticado'):
    st.error("Ingrese la contraseña")
    st.stop()      
    

    
