import streamlit as st
import pandas as pd
from github import Github
from io import BytesIO
import github
import io
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# Configuramos la página
st.set_page_config(
    page_title="Tablero de control/Calculadora Cuota Simple",
    page_icon="imgs/CAME-Transparente.ico.ico",
    )


st.title("Tablero de control")
st.header("Estadísticas")
st.write("Calculadora Cuota Simple")

@st.cache
def cargar_datos():
    datos_almacenados = pd.read_parquet("Datos almacenados/PRIMEROS 6000 DATOS.parquet")
    return datos_almacenados
    
def hide_password_input(input_label):
    password = st.text_input(input_label, type="password", key=input_label)
    return password

# Función para verificar la contraseña ingresada
def verificar_contraseña(contraseña):
    if contraseña == st.secrets["CONTRASENIA"]:
        return True
    elif contraseña == "0" or contraseña == "" or contraseña == " ": 
        pass
    elif contraseña != st.secrets["CONTRASENIA"]:
        return False
    else:
        pass

# ESTÁ FUNCION ES PARA CUANDO HAYA MÁS DE 13K DE DATOS
#@st.cache_data(persist=True)
#def cache_datos_completos (github_token, repo_name, file_path):
#    g = Github(github_token)
#    repo = g.get_repo(repo_name)
#    contents = repo.get_contents(file_path)
#    contents = repo.get_contents("CANTIDAD TOTAL DE REGISTROS.parquet")
#    # Create a file-like object from the decoded content
#    content_bytes = contents.decoded_content
#    content_file = io.BytesIO(content_bytes)
#    df2 = pd.read_parquet(content_file)   
#    return df2


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
    with st.spinner("Cargando . . ."):
        # ACCEDEMOS A LOS DATOS EN TIEMPO REAL
        github_token = st.secrets["TOKEN"] 
        repo_name = st.secrets["REPO"]
            
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(st.secrets["ARCHIVO_CALCULADORA"])
        # Create a file-like object from the decoded content
        content_bytes = contents.decoded_content
        content_file = io.BytesIO(content_bytes)
        # Read the CSV from the file-like object
        calculos = pd.read_csv(content_file)  
        # CALCULOS ANTERIORES
        datos_almacenados = cargar_datos()
        # CONCATENAMOS
        calculos = pd.concat([calculos,datos_almacenados])
        
        contents = repo.get_contents(st.secrets["ARCHIVO_CONSULTAS"])
        # Create a file-like object from the decoded content
        content_bytes = contents.decoded_content
        content_file = io.BytesIO(content_bytes)
        # Read the CSV from the file-like object
        consultas = pd.read_csv(content_file)  

        contents = repo.get_contents(st.secrets["ARCHIVO_CALIFICACION"]  )
        # Create a file-like object from the decoded content
        content_bytes = contents.decoded_content
        content_file = io.BytesIO(content_bytes)
        # Read the CSV from the file-like object
        calificaciones = pd.read_csv(content_file)  
        
        # Por si hay más datos (13k)
        #df2 = cache_datos_completos(github_token, repo_name, file_path)
        #df = pd.concat([df2,df1],ignore_index=True)
        
        # Generamos las tablas para los CÁLCULOS
        columnas = ["Provincia", "Programa", "Tipo de inscripcion" ]
        lista_tablas = []
        for elemento in columnas :     
            tabla = calculos[elemento].value_counts().reset_index().rename(columns={'count': 'N'})
            tabla["%"] = (tabla["N"] / tabla["N"].sum())*100
            tabla.loc[len(tabla)] = ["Total",tabla["N"].sum(),tabla["%"].sum()]
            tabla['%'] = tabla['%'].apply(lambda x: f'{x:.2f}%')
            lista_tablas.append(tabla)

        # Generamos las tablas para las calificaciones
        columnas = ["Evaluación"]
        lista_tablas2 = []
        for elemento in columnas :     
            tabla = calificaciones[elemento].value_counts().reset_index().rename(columns={'count': 'N'})
            tabla["%"] = (tabla["N"] / tabla["N"].sum())*100
            tabla.loc[len(tabla)] = ["Total",tabla["N"].sum(),tabla["%"].sum()]
            tabla['%'] = tabla['%'].apply(lambda x: f'{x:.2f}%')
            lista_tablas2.append(tabla)
        
    
        # DESCARGAR DATOS EN EXCEL
    
        def generar_excel():
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                calculos.to_excel(writer, sheet_name='Base', index=False)
                calificaciones.to_excel(writer, sheet_name='Base',  startcol=len(calculos.columns) + 2, index=False)
                consultas.to_excel(writer, sheet_name='Base',  startcol=len(calculos.columns) + len(calificaciones.columns) + 4, index=False)

                lista_tablas[0].to_excel(writer, sheet_name='Tablas', startrow=1, index=False)
                lista_tablas[1].to_excel(writer, sheet_name='Tablas', startrow=len(lista_tablas[0]) + 6, index=False)
                lista_tablas[2].to_excel(writer, sheet_name='Tablas', startrow=len(lista_tablas[0]) + 8 + len(lista_tablas[1]), index=False)
                lista_tablas2[0].to_excel(writer, sheet_name='Tablas', index=False,  startcol= len(lista_tablas[0].columns)+ 2)
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
    
        total_calculos = calculos.shape[0]
        st.write(f"### Cálculos totales: **{total_calculos}**")
    
        # Convertir la columna 'Fecha' al formato de fecha adecuado
        calculos['Fecha'] = pd.to_datetime(calculos['Fecha'], format='%d/%m/%y')
        # Agrupar por día y contar la cantidad de filas en cada grupo
        promedio_cantidad_calculos_por_dia = calculos.groupby(calculos['Fecha'].dt.date).size().mean()
        promedio_cantidad_calculos_por_dia = round(promedio_cantidad_calculos_por_dia,0)
        st.write(f"### Promedio de cantidad cálculos por dia: **{promedio_cantidad_calculos_por_dia}**")
    
        st.write("---")
    
        # CALCULOS POR DIA 
        st.header("Cantidad de cálculos por día")
        calculos_por_fecha = calculos["Fecha"].value_counts().reset_index().rename(columns={'count': 'N'})
        calculos_por_fecha = calculos_por_fecha.sort_values(by="Fecha",ascending=False)
        calculos_por_fecha['Fecha'] = calculos_por_fecha['Fecha'].dt.strftime('%d/%m/%y')
        # Seleccionar filtro
        fechas = ["Últimos 5 días", "Últimos 10 días", "Últimos 15 días", "Todos los días"]
        filtro_seleccionado2 = st.selectbox("Seleccione el periodo",fechas) 
        if filtro_seleccionado2 == "Últimos 5 días":
            calculos_por_fecha =  calculos_por_fecha.head()
        elif filtro_seleccionado2 == "Últimos 10 días":
            calculos_por_fecha =  calculos_por_fecha.head(10)
        elif filtro_seleccionado2 == "Últimos 15 días":
            calculos_por_fecha =  calculos_por_fecha.head(15)
        elif filtro_seleccionado2 == "Todos los días":
            calculos_por_fecha =  calculos_por_fecha
            
        calculos_por_fecha = calculos_por_fecha.to_html(index=False, escape = False)
        calculos_por_fecha = calculos_por_fecha.replace('<table border="1" class="dataframe">',
                                        '<table style="width: 100%; text-align: center;" border="1" class="dataframe">')
        calculos_por_fecha = calculos_por_fecha.replace('<th>', '<th style="text-align: center; background-color: blue; color: white;">')
        calculos_por_fecha = calculos_por_fecha.replace(f'<tr>\n      <td>Total</td>\n      <td>{total_calculos}</td>\n      <td>100.00%</td>\n    </tr>',
                                        f'<tr>\n      <td style="text-align: center; font-weight: bold;">Total</td>\n      <td style="text-align: center; font-weight: bold;">{total_calculos}</td>\n      <td style="text-align: center; font-weight: bold;">100.00</td>\n    </tr>')
        st.write(calculos_por_fecha, unsafe_allow_html=True)
        st.write("---")
        
        # Agrupa los datos por día y cuenta la cantidad de registros en cada día
        conteo_por_dia = calculos.groupby(calculos['Fecha'].dt.date)['Fecha'].count()
        
        # Seleccionar filtro
        fechas = ["Últimos 5 días", "Últimos 10 días", "Últimos 15 días", "Todos los días"]
        filtro_seleccionado = st.selectbox("Seleccione el filtro de fecha",fechas) 
        
        if filtro_seleccionado == "Últimos 5 días":
            conteo_por_dia =  conteo_por_dia.tail()
        elif filtro_seleccionado == "Últimos 10 días":
            conteo_por_dia =  conteo_por_dia.tail(10)
        elif filtro_seleccionado == "Últimos 15 días":
            conteo_por_dia =  conteo_por_dia.tail(15)
        elif filtro_seleccionado == "Todos los días":
            conteo_por_dia =  conteo_por_dia
            # Saltear de 5 en 5
            etiquetas_salteadas = range(0, len(conteo_por_dia.index), 10)
            nuevas_etiquetas = conteo_por_dia.index[etiquetas_salteadas]
    
        # GRAFICO DE CALCULOS POR DIA
    
        plt.figure(figsize=(10, 8))  # Ajusta el tamaño de la figura
        plt.plot(conteo_por_dia.index, conteo_por_dia.values, marker='o', linestyle='-', color='blue', linewidth=4)
        plt.grid(True)
        plt.title('Cantidad de cálculos por Día', fontsize=16)
        date_format = mdates.DateFormatter("%d/%m/%y")
        plt.gca().xaxis.set_major_formatter(date_format)
        if filtro_seleccionado == "Todos los días":
            plt.xticks(nuevas_etiquetas,rotation=90, ha='right')
        else:
            plt.xticks(conteo_por_dia.index,rotation=90, ha='right')
        plt.gcf().autofmt_xdate()  # Ajusta automáticamente las etiquetas
        plt.tight_layout()
        st.pyplot(plt)
        st.write("---")
        

        # CALIFICACIONES
        st.header("Consultas")
        st.dataframe(consultas)
        



        # CALIFICACIONES
        st.header("Valoraciones de la calculadora")
        calificaciones = lista_tablas2[0].to_html(index=False, escape = False)
        calificaciones = calificaciones.replace('<table border="1" class="dataframe">',
                                        '<table style="width: 100%; text-align: center;" border="1" class="dataframe">')
        calificaciones = calificaciones.replace('<th>', '<th style="text-align: center; background-color: blue; color: white;">')
        calificaciones = calificaciones.replace(f'<tr>\n      <td>Total</td>\n      <td>{len(lista_tablas2[0])}</td>\n      <td>100.00%</td>\n    </tr>',
                                        f'<tr>\n      <td style="text-align: center; font-weight: bold;">Total</td>\n      <td style="text-align: center; font-weight: bold;">{len(lista_tablas2[0])}</td>\n      <td style="text-align: center; font-weight: bold;">100.00</td>\n    </tr>')
        st.write(calificaciones, unsafe_allow_html=True)
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


