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

colA, colB = st.columns([1,2])
with colA :
    st.image("imgs/CAME-Transparente.png", use_column_width=True, width=600)
# Imagen común a todas las páginas ya que esta por fuera de las funciones
with colB : 
    contraseña = hide_password_input("Ingrese la contraseña:")
       

st.write("---")

# Verificar la contraseña
if verificar_contraseña(contraseña) == True:
    st.success("Contraseña válida. Acceso concedido.")
    # Establecer el estado de autenticación de la sesión
    st.session_state.autenticado = True

    aux_contra = True
    # Creamos la conexión
else:
    st.error('Contraseña no válida.')  

st.write("---")

if not st.session_state.get('autenticado'):
    st.error("Ingrese la contraseña")
    st.stop()      

if aux_contra == True :     
    # ACCEDEMOS A LOS DATOS EN TIEMPO REAL
    github_token = st.secrets["TOKEN"] 
    repo_name = st.secrets["REPO"]
    file_path = st.secrets["ARCHIVO"]   
        
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    contents = repo.get_contents(file_path)
    # Create a file-like object from the decoded content
    content_bytes = contents.decoded_content
    content_file = io.BytesIO(content_bytes)
    # Read the CSV from the file-like object
    df = pd.read_csv(content_file)   

    # Generamos las tablas
    columnas = ["Provincia", "Programa", "Tipo de inscripcion" ]
    lista_tablas = []
    for elemento in columnas :     
        tabla = df[elemento].value_counts().reset_index().rename(columns={'count': 'N'})
        tabla["%"] = (tabla["N"] / tabla["N"].sum())*100
        tabla.loc[len(tabla)] = ["Total",tabla["N"].sum(),tabla["%"].sum()]
        tabla['%'] = tabla['%'].apply(lambda x: f'{x:.2f}%')
        lista_tablas.append(tabla)
    

    col1, col2 = st.columns(2)
    with col1:
        total_calculos = df.shape[0]
        st.write(f"Cálculos totales: {total_calculos}")

    with col2:
        # Convertir la columna 'Fecha' al formato de fecha adecuado
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%y')
        # Agrupar por día y contar la cantidad de filas en cada grupo
        promedio_cantidad_calculos_por_dia = df.groupby(df['Fecha'].dt.date).size().mean()
        promedio_cantidad_calculos_por_dia = round(promedio_cantidad_calculos_por_dia,0)
        st.write(f"Promedio de cantidad cálculos por dia: {promedio_cantidad_calculos_por_dia}")

    st.write("---")

    st.write("Cálculos por provincia")
    calculos_por_provincia = lista_tablas[0].to_html(index=False)
    st.write(calculos_por_provincia, unsafe_allow_html=True)
    st.write("---")

    st.write("Cálculos por programa")
    calculos_por_programa = lista_tablas[1].to_html(index=False, escape=False)
    calculos_por_programa = calculos_por_programa.replace('<table border="1" class="dataframe">',
                                    '<table style="width: 100%; text-align: center;" border="1" class="dataframe">')
    calculos_por_programa = calculos_por_programa.replace('<th>', '<th style="text-align: center; background-color: blue; color: white;">')
    
    # Modificar manualmente la última fila para aplicar estilos
    calculos_por_programa = calculos_por_programa.replace('<tr>\n      <td>Total</td>\n      <td>1908</td>\n      <td>100.00</td>\n    </tr>',
                                    '<tr style="background-color: #FFE4B5; font-weight: bold;">\n      <td style="text-align: center;">Total</td>\n      <td style="text-align: center;">1908</td>\n      <td style="text-align: center;">100.00</td>\n    </tr>')
    
    # Mostrar la tabla en Streamlit
    st.write(calculos_por_programa, unsafe_allow_html=True)
    st.write("---")

    st.write("Cálculos por tipo de inscripción")
    calculos_por_tipo_inscripcion = lista_tablas[2].to_html(index=False)
    st.write(calculos_por_tipo_inscripcion, unsafe_allow_html=True)
    st.write("---")

    st.write("Base")
    st.dataframe(df)
