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
 - **Tag V3.0** Cuarto entregable: Script de tercera entrega con DAG parametrizado y alerta por correo

## Implementación

### Resumen
  Este proyecto incluye el uso del [Tech-stack](#tech-stack) para elaborar un ETL con un check de datos y alerta por medio de email, todo mediante un DAG de airflow embebido en contenedores de docker. El ETL extrae datos desde una API llamada TwleveData, la cual extrae información de precios de stock específicamente de Amazon, Disney y Apple. Después los transforma utilizando herramientas de python y los carga en AWS Redshift. En el DAG existen un par de tasks despues del ETL, los cuales hacen un chequeo de valores para el precio promedio del stock y otro task para mandar alerta de email en caso de que el chequeo se encuentre fuera de los límites.

  > **Important**
  > Mas que utilizar las mejores prácticas en cuanto al uso de de las herramientas, se exploran diferentes formas de llegar a un mismo objetivo con el propósito de practicar o de tener un proyecto que a futuro, pueda servir como referencia. Entre estos métodos, podremos encontrar diferentes formas de conectarnos a Redshift, almacenaje de información sensible como credenciales y el uso de distintos operadores. 

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
  - .gitignore: Reglas que contienen archivos y carpetas a tracker o no trackear por git
  - .env: Este archivo contiene las credenciales de Redshift y la key de la API de TwelveData en forma de llave valor. Al clonar el repo, el **usuario debera crear este archivo**, mismo que debe contener las siguientes variables con sus respectivos valores CREDS_REDSHIFT_HOST, CREDS_REDSHIFT_DATABASE, CREDS_REDSHIFT_PORT, CREDS_REDSHIFT_USER, CREDS_REDSHIFT_PASSWORD y TWELVE_DATA_API_KEY. Ejemplo TWELVE_DATA_API_KEY=872345447357f
  - email.png: Screenshot del correo alerta recibido, parte de entregable final
- **/airflow/** contiene las carpetas que airflow necesita durante su ejecución 
- **/airflow/dags/** contiene utilidades y el DAG a ejecutar
  - twelve_data.py: DAG completo con los pasos de entregables
- **/airflow/dags/utils/** contiene archivos que solo utiliza el DAG twelve_data.py
  - airflow.png: imagen utilizada por el correo de alerta
  - body.html: contenido html del correo de alerta
  - functions.py: functiones de tasks utilizados en el DAG twelve_data.py
- **/airflow/logs/** Contiene los logs de las ejecuciones de los dags que se visualizan en la UI. Inicialmente se encontrará vacío.
- **/airflow/plugins/** Funcionalidades extras sobre airflow, de momento no hay.
- **/app/** contiene el todo lo relacionado con la aplicación.
  - Dockerfile: Contiene la configuracion para hacer el build de la imagen de airflow con python 3.11
  - main.py: Contiene el código que ejecuta las funciones obtenidas del directorio libs/
  - requirements.txt: Contiene las librerías adicionales requeridas por la app que se instalarán en la imagen de docker
- **/app/libs/** codigo adicional utilizado por la app.
  - api.py: Funciones relacionadas a la extracción de datos por medio de la api de TwelveData.
  - db_engine.py: Funciones relacionadas a la conexión hacia la db de Redshift.
  - sql_queries.py: Queries para crear y/o eliminar tablas en Redshift.
  - avg_threshold.sql: Query para obtener el precio promedio segun el stock, start_date y end_date proporcionados


### Pasos para su ejecución

  > **Important**
  > Para las credenciales de la API, se necesita crear una cuenta y obtener un API Key de Twelve Data. Twelve Data provee datos históricos financieros sobre stocks, criptomonedas etc. Para las credenciales de Redshift, es necesario que el team de Coderhouse genere las mismas para acceder a la base de datos. En este repositorio remoto no existen ni se subirán credenciales por cuestiones de seguridad.

  1. Instalar Docker Desktop y Docker Compose segun tu SO, la última versión de ambos debería de funcionar bien. 
  2. Forkear o clonar este repositorio de Github
  3. Correr Docker Desktop y/o asegurarse que el agente de Docker se encuentra corriendo. 
  4. Crear el archivo .env en el root y agregar las variables mencionadas en [Project Tree](#project-tree)
  5. Abrir una terminal y cambiar el directorio a  **_coderhouse-proyecto/app/_**
      ```console
      foo@bar:~$ cd coderhouse-proyecto/app
      ```
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
  11. Antes de hacer algún tipo de ejecución, es importante crear variables en la UI de airflow (Admin > Variables) para la conexion através de SMTP y que puedas recibir el correo de alerta. Las variables a crear deberan llamarse SECRET_SMTP_EMAIL, SECRET_SMTP_PWD_EMAIL, SMTP_PORT_EMAIL y SMTP_HOST_EMAIL. El prefijo SECRET_ permitirá que la UI muestre el valor de las variables con asteriscos. 
      > **Nota**
      > Existen varias formas de crear configuraciones SMTP, en este caso se crea utilizando la librería SMPT y utilizando variables de airflow, por lo que no es necesario modificar el airflow.cfg. 
      > **Important**
      > Es importante consultar y realizar los cambios necesarios en la configuracion a la cuenta de correo que se utilice, para que pueda ser capaz de recibir correos por medio de SMTP. Dependiendo del host será la configuración. Para este ejercicio, se utiliza outlook (credenciales no proporcionadas).
  12. En la misma UI de airflow, se debe de crear la conexión a redshift. En el archivo .env se tienen las credenciales, sin embargo, otro método para generar la conexión es utilizando la UI  de airflow (Admin > Connections). 
      > **Nota**
      > En este caso, las credenciales son proporcionadas por el team de Coderhouse. En cualquier conexión se deberá tener host, user, password y port. Lo importante es que el nombre de la conexión se mantenga como **redshift_default**.  
  13. Para ejecutar el DAG, click en la pestaña de DAGs, aquí deberá aparecer el DAG del proyecto llamado twelve_data_stock. En el DAG, hasta la izquierda aparecerá un botón de play. Al hacer click nos muestra opciones para lanzarlo con valores default o lanzarlo con una configuración customizada. Si seleccionamos la configuracion customizada, podremos introducir valores que necesitemos para la ejecución.
      > **Important**
      > Para fines prácticos, los datos del ETL se limitan a la carga de 3 stocks: Amazon -- "AMZN", Disney -- "DIS" y Apple -- "AAPL", y en un rango de datos que van del "2020-01-01" al "2020-12-31". **Los parametros de entrada que podemos customizar se utilizan para calcular el promedio de precio de un solo stock segun el rango de fechas introducido**. Por default, este cálculo se hace para el stock "AMZN", rango de fechas start_date "2020-01-01" al end_date "2020-12-31", valor de threshold minimo y maximo th_min 130 y th_max 150 respectivamente.
  14. Una vez ejecutado el DAG, podemos ir a la pantalla de Graph o Grid para monitorear su ejecución, así como ver los logs disponibles en caso de error. 
  15. Para detener el cluster, podemos ejecutar el comando `docker compose down` en otra terminal, o utilizar CTRL-C para detener el proceso en la misma terminal de ejecución. 
      ```console
      foo@bar:~$ docker compose down
      ```
