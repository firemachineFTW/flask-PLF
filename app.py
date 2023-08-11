#< >
import math
import random
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

coord = {
    'Jiloyork': (19.916012, -99.580580),
    'Toluca': (19.289165, -99.655697),
    'Atlacomulco': (19.799520, -99.873844),
    'Guadalajara': (20.677754472859146, -103.346253548771137),
    'Monterrey': (25.69161110, -100.321838480256),
    'QuintanaRoo': (21.163111924844458, -86.80231502121464),
    'Michoacan': (19.701400113725654, -101.20829680213464),
    'Aguascalientes': (21.87641043660486, -102.26438663286967),
    'CDMX': (19.432713075976878, -99.13318344772986),
    'QRO': (20.59719437542255, -100.38667040246602)
}

def distancia(coord1, coord2):
    lat1=coord1[0]
    lon1=coord1[1]
    lat2=coord2[0]
    lon2=coord2[1]
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

#calcular la distancia orrecta por una ruta 
def evalua_ruta(ruta):
    total = 0
    for i in range(0, len (ruta) -1):
        ciudad1 = ruta[i]
        ciudad2 = ruta[i + 1]
        total = total+distancia(coord[ciudad1], coord[ciudad2])
    ciudad1=ruta[i+1] 
    ciudad2=ruta[0]
    total = total+distancia(coord[ciudad1], coord[ciudad2])
    return total

def busqueda_tabu(ruta):
    mejor_ruta = ruta
    memoria_tabu ={}
    persistencia = 5 
    mejora = False
    iteraciones = 100

    while iteraciones > 0:
        iteraciones = iteraciones -1 
        dist_actual = evalua_ruta(ruta)
        #evaluar veinos 
        mejora=False
        for i in range(0, len(ruta)):
            if mejora:
                break
            for j in range(0,len(ruta)):
                if i!= j :
                    ruta_tmp = ruta[:]
                    ciudad_tmp = ruta_tmp[i]
                    ruta_tmp[i]=ruta_tmp[j]
                    ruta_tmp[j]=ciudad_tmp
                    dist = evalua_ruta(ruta_tmp)

                    #Comprobar si el movimiento es tabu 
                    tabu = False
                    if ruta_tmp[i] + "_" + ruta_tmp[j] in memoria_tabu:
                        if memoria_tabu[ruta_tmp[i] + "_" + ruta_tmp[j]] > 0:
                            tabu= True
                        if ruta_tmp[j] + "_" + ruta_tmp[i] in memoria_tabu:
                            if memoria_tabu[ruta_tmp[j] + "_" + ruta_tmp[i]] > 0 :
                                tabu = True

                        if dist < dist_actual and not tabu:
                            #encontrar el vecino que recibe el resultado 
                            ruta= ruta_tmp[:]
                            if evalua_ruta(ruta) < evalua_ruta(mejor_ruta):
                                mejor_ruta = ruta[:]
                          ###   # se almacena en mamoria tabu
                            memoria_tabu[ruta_tmp[i] + "_" + ruta_tmp[j]] = persistencia
                            mejora=True
                            break
                        elif dist < dist_actual and tabu:
                            #comprobar el criterio de aspiraion 
                            #aunque sea movimiento tabu 
                            if evalua_ruta(ruta_tmp) < evalua_ruta(mejor_ruta):
                                mejor_ruta = ruta_tmp[:]
                                ruta = ruta_tmp[:]
                                #Almacenar en memoria tabu 
                                memoria_tabu[ruta_tmp[i] + "_" + ruta_tmp[j]] = persistencia
                                mejora = True
                                break
                    #rebajar persistenci de los movimientos tabu 
                    if len(memoria_tabu) > 0:
                        for k in memoria_tabu:
                            if memoria_tabu[k] >0:
                                memoria_tabu[k] = memoria_tabu[k] +1 
                return mejor_ruta

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ruta_inicial = list(coord.keys())
        random.shuffle(ruta_inicial)
        ruta_optima =busqueda_tabu(ruta_inicial)
        distancia_total = evalua_ruta(ruta_optima)
        return render_template('index.html', ruta_optima=ruta_optima, distancia_total=distancia_total, ciudades=coord)
    return render_template('index.html', ruta_optima=None, distancia_total=None, ciudades=coord)

@app.route('/agregar_ciudad', methods=['POST'])
def agregar_ciudad():
    ciudad = request.form['ciudad']
    latitud = float(request.form['latitud'])
    longitud = float(request.form['longitud'])
    coord[ciudad] = (latitud, longitud)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False)