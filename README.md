# Coderhouse - Data Engineering Flex

## Table of Contents  
- [Entregables](#entregables) 
- [Implementación](#implementación)  
- [Resumen](#resumen) 
- [Tech-stack](#tech-stack)
- [Project Tree](#project-tree)
- [Pasos para su ejecución](#pasos-para-su-ejecución)

## Entregables
 - **Tag V0.0** Primer entregable: Script que extraiga datos de una API pública y creación de tabla en Redshift
 - **Tag V1.1** Segundo entregable: Script de primera entrega con carga de datos hacia AWS Redshift
 - **Tag V2.1** Tercer entregable: Script de segunda entrega dentro de un contenedor de Docker y un DAG de Apache Airflow

## Implementación

### Resumen
  Pendiente

### Tech-stack
- Python
- Postgres DB
- Docker
- Git
- Apache Airflow
- TwelveData API

### Project Tree

- Directorio root **coderhouse-proyecto/**
  - README.me: Archivo que contiene información del proyecto
  - docker-compose.yaml: Archivo que utiliza la imagen creada en el Dockerfile y levanta servicios para el funcionamiento de Airflow
- **/airflow/** contiene las carpetas que airflow necesita durante su ejecución 
  - /dags/TwelveData.py: DAG que ejecuta la app mediante un BashOperator.
  - /logs/: Contiene los logs de las ejecuciones de los dags que se visualizan en la UI. Inicialmente se encontrará vacío.
  - /plugins/: Funcionalidades extras sobre airflow, de momento no hay.
- **/app/** contiene el todo lo relacionado con la aplicación.
  - Dockerfile: Contiene la configuracion para hacer el build de la imagen de airflow con puthon 3.11
  - main.py: Contiene el código que ejecuta las funciones obtenidas del directorio libs/
  - requirements.txt: Contiene las librerías adicionales requeridas por la app que se instalarán en la imagen de docker
  - credentials.py: Este python contiene las credenciales para la db de Redshift, así como las de TwelveData. El usuario deberá crear este archivo para que la app funcione correctamente.
- **/app/libs/** codigo adicional utilizado por la app.
  - api.py: Funciones relacionadas a la extracción de datos por medio de la api de TwelveData.
  - db_engine.py: Funciones relacionadas a la conexión hacia la db de Redshift.
  - sql_queries.py: Queries para crear y/o eliminar tablas en Redshift.


### Pasos para su ejecución

  > **Importante**
  > Para las credenciales de la API, se necesita crear una cuenta y obtener un API Key de Twelve Data. Twelve Data provee datos históricos financieros sobre stocks, criptomonedas etc. Para las credenciales de Redshift, es necesario que el team de Coderhouse genere las mismas para acceder a la base de datos. En este repositorio remoto no existen ni se subirán credenciales por cuestiones de seguridad.

  1. Instalar Docker Desktop y Docker Compose segun tu SO, la última versión de ambos debería de funcionar bien. 
  2. Forkear o clonar este repositorio de Github
  3. Correr Docker Desktop y/o asegurarse que el agente de Docker se encuentra corriendo. 
  4. Abrir una terminal y cambiar el directorio a  **_coderhouse-proyecto/app/_**
      ```console
      foo@bar:~$ cd coderhouse-proyecto/app
      ```
  5. Crear el archivo credentials.py y agregar la API Key a la variable TWELVE_DATA_API_KEY como string y las credenciales de redshift a la variable CREDS_REDSHIFT como diccionario, donde las llaves serán el HOST, DATABASE, PORT, USER y PASSWORD. 
  6. En el mismo directorio, ejecutar el comando `docker build . -t coderhouse-proyecto`, el cual creará la imagen de docker de airflow con python 3.11 que se necesita, adicionando la instalación de los módulos mencionados en el archivo requirements.txt. La imagen la podremos ver con el nombre coderhouse-proyecto utilizando el comando `docker images`. 
      > **Nota**
      > La creación de la imagen solo se tiene que hacer una vez, a menos que se borre la imagen. 
  
      ```console
      foo@bar:~$ docker build . -t coderhouse-proyecto
      ```
      ```console
      foo@bar:~$ docker images
      ```
  7.  Cambiar el directorio de trabajo al directorio root del proyecto coderhouse-proyecto, el cual se encontrará un nivel arriba. 
      ```console
      foo@bar:~$ cd ..
      ```
  8. Ejecutar el comando `docker compose up` para levantar Apache Airflow junto con los servicios que requiere. Este docker compose se compone de la imagen que creamos en pasos previos, así como la descarga de una imagen de Postgres, mismo que Airflow utiliza para su funciónalidad. 
      ```console
      foo@bar:~$ docker compose up
      ```
      > **Nota**
      > Se puede utilizar el comando  `docker compose up -d` si no se desea ver los logs de ejecución en la terminal. 
  9. Una vez que en la terminal se muestre el mensaje: __coderhouse-proyecto-airflow-init-1 exited with code 0__, la inicialización está lista y podemos acceder a la UI de Airflow, así como ver los contenedores de los servicios de airflow activos, los cuales deberán de ser **Postgres-1**, **airflow-scheduler-1** y **airflow-webserver-1**. El servicio **airflow-init-1** se encontrará inactivo.
  10. Mediante un Explorador Web, podemos acceder a http://localhost:8080/home, mismo que desplegará el login de Airflow. Las credenciales son las mismas que se encuentra en el archivo de docker-compose.yaml. Aquí podremos visualizar la ejecución del DAG, así como ejecuciones previas y próximas según el scheduler.
  11. En el DAG, podemos acceder a alguna ejecución para visualizar el log y verificar que el ETL se realizó de forma exitosa, además de acceder a la tabla en Redshift para comprobar los datos nuevos. 
  11. Para detener el cluster, podemos ejecutar el comando `docker compose down` en otra terminal, o utilizar CTRL-C para detener el proceso en la misma terminal de ejecución. 
      ```console
      foo@bar:~$ docker compose down
      ```
