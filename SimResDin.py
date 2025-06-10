import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from numpy.polynomial import polynomial as P  # Añadir importación para multiplicar polinomios

st.set_page_config(page_title="Simulador de Respuesta Dinámica", layout="centered")

st.title("Simulador de Respuesta de Sistemas de Primer y Segundo Orden")

st.markdown("""
Este simulador permite explorar la respuesta temporal de sistemas de primer y segundo orden.
Ajusta los parámetros y observa cómo cambia la respuesta.
""")

# Selección de tipo de sistema
order = st.radio("Selecciona el orden del sistema:", [1, 2])

# Entradas comunes
input_type = st.selectbox("Selecciona el tipo de entrada:", ["Escalón", "Impulso"])

# Nueva entrada para la amplitud de la señal (ANTES de usarla)
amplitude = st.slider("Amplitud de la señal de entrada", min_value=0.1, max_value=10.0, value=1.0, step=0.1)

if order == 1:
    k = st.slider("Ganancia estática (k)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
    tau = st.slider("Constante de tiempo (tau) [s]", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
    num = [k]
    den = [tau, 1]
    system = signal.TransferFunction(num, den)
else:
    wn = st.slider("Frecuencia natural (wn) [rad/s]", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
    zeta = st.slider("Coeficiente de amortiguamiento (zeta)", min_value=0.0, max_value=2.0, value=0.5, step=0.05)
    num = [wn**2]
    den = [1, 2*zeta*wn, wn**2]
    system = signal.TransferFunction(num, den)

# Mostrar la función de transferencia
st.subheader("Función de Transferencia del Sistema")
numerator = np.poly1d(num)
denominator = np.poly1d(den)

# Expresión en orden decreciente de potencias de s
num_str = '+'.join(
    f'{coef} s^{len(num)-i-1}' if len(num)-i-1 > 0 else f'{coef}'
    for i, coef in enumerate(num)
)
den_str = '+'.join(
    f'{coef} s^{len(den)-i-1}' if len(den)-i-1 > 0 else f'{coef}'
    for i, coef in enumerate(den)
)
delay_str = ''

st.latex(r'G(s) = \frac{' + num_str + r'}{' + den_str + r'}' + delay_str)

# Mostrar U(s) (entrada)
st.subheader("Función de Entrada U(s)")
if input_type == "Escalón":
    st.latex(r'U(s) = \frac{' + f'{amplitude}' + r'}{s}')
else:  # Impulso
    st.latex(r'U(s) = ' + f'{amplitude}')

# Mostrar Y(s) (salida)
st.subheader("Función de Salida Y(s)")
if input_type == "Escalón":
    st.latex(r'Y(s) = G(s) \times U(s) = \frac{' + f'({amplitude})(' + num_str + r')}{s(' + den_str + r')}')
else:  # Impulso
    st.latex(r'Y(s) = G(s) \times U(s) = \frac{' + f'({amplitude})(' + num_str + r')}{' + den_str + r'}')

# Tiempo de simulación
t_end = 10
t = np.linspace(0, t_end, 1000)

# Generar respuesta (antes de aplicar retardo simple)
if input_type == "Escalón":
    t_resp, y_resp = signal.step(system, T=t)
else:
    t_resp, y_resp = signal.impulse(system, T=t)

y_resp = amplitude * y_resp

y = y_resp

# Gráfica
fig, ax = plt.subplots(figsize=(10, 6))

# Definir la señal de entrada
if input_type == "Escalón":
    u = np.zeros_like(t)
    u[t > 0] = amplitude
else:
    u = np.zeros_like(t)
    u[t == 0] = amplitude

ax.plot(t, u, label='Entrada', linestyle='dotted', color='orange')
ax.plot(t, y, label='Respuesta')

# Añadir marca del valor en estado estacionario
if order == 1:
    final_value = k * amplitude if input_type == "Escalón" else 0
else:
    final_value = amplitude if input_type == "Escalón" else 0

ax.axhline(y=final_value, color='gray', linestyle='dashed', label=f'Valor final = {final_value}')

# Añadir marcas y anotaciones
if order == 1:
    # Para primer orden: marcar tau y valor de k
    try:
        idx_tau = (np.abs(t - tau)).argmin()
        ax.plot(t[idx_tau], y[idx_tau], 'ro', label=f'τ = {tau:.2f}s')
        ax.vlines(x=t[idx_tau], ymin=0, ymax=y[idx_tau], linestyles='dashed', colors='red')
        ax.hlines(y=y[idx_tau], xmin=0, xmax=t[idx_tau], linestyles='dashed', colors='red')
        ax.text(t[idx_tau] + 0.5, y[idx_tau], f'τ = {tau:.2f}s\n(62.3% del valor final)', color='red', fontsize=9)
        ax.axhline(y=k, color='g', linestyle='--', label=f'Ganancia (k) = {k}')
        ax.hlines(y=k, xmin=0, xmax=t_end, linestyles='dashed', colors='green')
        ax.text(t_end * 0.6, k + amplitude * 0.1, f'k = {k}', color='green', fontsize=9)
    except:
        pass
else:
    # Para segundo orden: marcar tiempos de establecimiento Ts para 2% y 5% basados en el 98% y 95% del valor final,
    # y marcar el overshoot si zeta < 1
    if zeta < 1:
        final_value = amplitude  # Asumiendo que el valor final es la amplitud de entrada para sistemas escalón
        target_98 = 0.98 * final_value
        target_95 = 0.95 * final_value
        try:
            idx_Ts_2 = (np.abs(y - target_98)).argmin()
            idx_Ts_5 = (np.abs(y - target_95)).argmin()
            idx_max = y.argmax()
            if y[idx_max] > final_value:
                overshoot_percentage = ((y[idx_max] - final_value) / final_value) * 100
                # Marcar y anotar el overshoot
                # Marcar y anotar el overshoot como flecha bidireccional vertical
                ax.plot(t[idx_max], y[idx_max], 'bo', label=f'Overshoot ≈ {overshoot_percentage:.2f}%')
                ax.annotate(
                    '',
                    xy=(t[idx_max], final_value),
                    xytext=(t[idx_max], y[idx_max]),
                    arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5)
                )
                ax.text(t[idx_max] + 0.5, (y[idx_max] + final_value) / 2, f'Overshoot ≈ {overshoot_percentage:.2f}%', color='blue', fontsize=9, ha='center')
                if t[idx_Ts_2] > t[idx_max]:
                    ax.plot(t[idx_Ts_2], y[idx_Ts_2], 'ro', label=f'Ts (2%) ≈ {t[idx_Ts_2]:.2f}s')
                    ax.vlines(x=t[idx_Ts_2], ymin=0, ymax=y[idx_Ts_2], linestyles='dashed', colors='red')
                    ax.hlines(y=y[idx_Ts_2], xmin=0, xmax=t[idx_Ts_2], linestyles='dashed', colors='red')
                    ax.text(t[idx_Ts_2] + 0.5, y[idx_Ts_2], f'Ts (2%) ≈ {t[idx_Ts_2]:.2f}s', color='red', fontsize=9)
                if t[idx_Ts_5] > t[idx_max]:
                    ax.plot(t[idx_Ts_5], y[idx_Ts_5], 'mo', label=f'Ts (5%) ≈ {t[idx_Ts_5]:.2f}s')
                    ax.vlines(x=t[idx_Ts_5], ymin=0, ymax=y[idx_Ts_5], linestyles='dashed', colors='magenta')
                    ax.hlines(y=y[idx_Ts_5], xmin=0, xmax=t[idx_Ts_5], linestyles='dashed', colors='magenta')
                    ax.text(t[idx_Ts_5] + 0.5, y[idx_Ts_5], f'Ts (5%) ≈ {t[idx_Ts_5]:.2f}s', color='magenta', fontsize=9)
        except:
            pass

ax.set_title(f"Respuesta al {input_type}")
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Salida")
ax.set_xlim(left=-0.5, right=t_end + 0.5)
ax.set_ylim(bottom=-0.1 * amplitude, top=1.2 * max(y.max(), amplitude))
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Cálculo de métricas
st.subheader("Métricas del Sistema")

if order == 1:
    st.write(f"**Ganancia estática (k):** {k}")
    st.write(f"**Constante de tiempo (tau):** {tau} s")
else:
    st.write(f"**Frecuencia natural no amortiguada (wn):** {wn:.2f} rad/s")
    st.write(f"**Coeficiente de amortiguamiento (zeta):** {zeta:.2f}")
    if zeta < 1:
        Ts = 4 / (zeta * wn)
        Mp = np.exp(-zeta * np.pi / np.sqrt(1 - zeta**2)) * 100
        st.write(f"**Tiempo de establecimiento (Ts):** {Ts:.2f} s")
        st.write(f"**Sobreimpulso máximo (Mp):** {Mp:.2f} %")
    else:
        st.write("Sistema sobreamortiguado: no hay sobreimpulso ni tiempo de establecimiento definido.")

st.markdown("""
---
Este simulador ha sido desarrollado como material docente para la asignatura **Regulación Automática de la Universidad de Cádiz**.
""")