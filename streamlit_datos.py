import streamlit as st
import pandas as pd
from github import Github
from io import BytesIO
import github
import io

st.title("Tablero de control")
st.header("Estadísticas")
st.write("Calculadora Ahora 12")

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
elif verificar_contraseña(contraseña) == False:
    st.error('Contraseña no válida.')  

else:
    pass

st.write("---")

if not st.session_state.get('autenticado'):
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
    

    # DESCARGAR DATOS EN EXCEL

    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Base', index=False)
            lista_tablas[0].to_excel(writer, sheet_name='Tablas', startrow=1, index=False)
            lista_tablas[1].to_excel(writer, sheet_name='Tablas', startrow=len(lista_tablas[0]) + 6, index=False)
            lista_tablas[2].to_excel(writer, sheet_name='Tablas', startrow=len(lista_tablas[0]) + 8 + len(lista_tablas[1]), index=False)
        output.seek(0)
        return output

    excel_data = generar_excel()
        
    # Descargar el archivo desde la memoria
    st.download_button(
        label='Descargar datos en Excel',
        data=excel_data,
        key='archivo_excel',
        file_name='datos_calculadora.xlsx',
        )

    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        total_calculos = df.shape[0]
        st.write(f"+ ### Cálculos totales: **{total_calculos}**")

    with col2:
        # Convertir la columna 'Fecha' al formato de fecha adecuado
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%y')
        # Agrupar por día y contar la cantidad de filas en cada grupo
        promedio_cantidad_calculos_por_dia = df.groupby(df['Fecha'].dt.date).size().mean()
        promedio_cantidad_calculos_por_dia = round(promedio_cantidad_calculos_por_dia,0)
        st.write(f"+ ### Promedio de cantidad cálculos por dia: **{promedio_cantidad_calculos_por_dia}**")

    st.write("---")

    # CALCULOS POR DIA 
    st.header("Cantidad de cálculos por día")
    calculos_por_fecha = df["Fecha"].value_counts().reset_index().rename(columns={'count': 'N'})
    calculos_por_fecha['Fecha'] = calculos_por_fecha['Fecha'].dt.strftime('%d/%m/%y')
    calculos_por_fecha = calculos_por_fecha.sort_values(by="Fecha",ascending=False)
    calculos_por_fecha = calculos_por_fecha.to_html(index=False, escape = False)
    calculos_por_fecha = calculos_por_fecha.replace('<table border="1" class="dataframe">',
                                    '<table style="width: 100%; text-align: center;" border="1" class="dataframe">')
    calculos_por_fecha = calculos_por_fecha.replace('<th>', '<th style="text-align: center; background-color: blue; color: white;">')
    calculos_por_fecha = calculos_por_fecha.replace(f'<tr>\n      <td>Total</td>\n      <td>{total_calculos}</td>\n      <td>100.00%</td>\n    </tr>',
                                    f'<tr>\n      <td style="text-align: center; font-weight: bold;">Total</td>\n      <td style="text-align: center; font-weight: bold;">{total_calculos}</td>\n      <td style="text-align: center; font-weight: bold;">100.00</td>\n    </tr>')
    st.write(calculos_por_fecha, unsafe_allow_html=True)
    st.write("---")

    

    # PROVINCIA
    st.header("Cantidad de cálculos por provincia")
    calculos_por_provincia = lista_tablas[0].to_html(index=False, escape = False)
    calculos_por_provincia = calculos_por_provincia.replace('<table border="1" class="dataframe">',
                                    '<table style="width: 100%; text-align: center;" border="1" class="dataframe">')
    calculos_por_provincia = calculos_por_provincia.replace('<th>', '<th style="text-align: center; background-color: blue; color: white;">')
    calculos_por_provincia = calculos_por_provincia.replace(f'<tr>\n      <td>Total</td>\n      <td>{total_calculos}</td>\n      <td>100.00%</td>\n    </tr>',
                                    f'<tr>\n      <td style="text-align: center; font-weight: bold;">Total</td>\n      <td style="text-align: center; font-weight: bold;">{total_calculos}</td>\n      <td style="text-align: center; font-weight: bold;">100.00</td>\n    </tr>')
    st.write(calculos_por_provincia, unsafe_allow_html=True)
    st.write("---")

    # PROGRAMA
    st.header("Cantidad de cálculos por programa")
    calculos_por_programa = lista_tablas[1].to_html(index=False, escape=False)
    calculos_por_programa = calculos_por_programa.replace('<table border="1" class="dataframe">',
                                    '<table style="width: 100%; text-align: center;" border="1" class="dataframe">')
    calculos_por_programa = calculos_por_programa.replace('<th>', '<th style="text-align: center; background-color: blue; color: white;">')
    calculos_por_programa = calculos_por_programa.replace(f'<tr>\n      <td>Total</td>\n      <td>{total_calculos}</td>\n      <td>100.00%</td>\n    </tr>',
                                    f'<tr>\n      <td style="text-align: center; font-weight: bold;">Total</td>\n      <td style="text-align: center; font-weight: bold;">{total_calculos}</td>\n      <td style="text-align: center; font-weight: bold;">100.00</td>\n    </tr>')
    st.write(calculos_por_programa, unsafe_allow_html=True)
    st.write("---")

    # TIPO DE INSCRIPCION
    st.header("Cantidad de cálculos por tipo de inscripción")
    calculos_por_tipo_inscripcion = lista_tablas[2].to_html(index=False, escape = False)
    calculos_por_tipo_inscripcion = calculos_por_tipo_inscripcion.replace('<table border="1" class="dataframe">',
                                    '<table style="width: 100%; text-align: center;" border="1" class="dataframe">')
    calculos_por_tipo_inscripcion = calculos_por_tipo_inscripcion.replace('<th>', '<th style="text-align: center; background-color: blue; color: white;">')
    calculos_por_tipo_inscripcion = calculos_por_tipo_inscripcion.replace(f'<tr>\n      <td>Total</td>\n      <td>{total_calculos}</td>\n      <td>100.00%</td>\n    </tr>',
                                    f'<tr>\n      <td style="text-align: center; font-weight: bold;">Total</td>\n      <td style="text-align: center; font-weight: bold;">{total_calculos}</td>\n      <td style="text-align: center; font-weight: bold;">100.00</td>\n    </tr>')
    st.write(calculos_por_tipo_inscripcion, unsafe_allow_html=True)
    st.write("---")
