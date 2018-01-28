# https://github.com/jostmey/NakedTensor/blob/master/serial.py
# Fit a straight line, of the form y=m*x+b

import tensorflow as tf

def fit_line():
    xs = [ 0.00,  1.00,  2.00, 3.00, 4.00, 5.00, 6.00, 7.00] # Features
    ys = [-0.82, -0.94, -0.12, 0.26, 0.39, 0.64, 1.02, 1.00] # Labels

    m_initial = -0.5
    b_initial =  1.0
    m = tf.Variable(m_initial)
    b = tf.Variable(b_initial)

    total_error = 0.0
    for x, y in zip(xs, ys):
        y_model = m*x + b
        total_error += (y-y_model)**2

    optimizer_operation = tf.train.GradientDescentOptimizer(learning_rate=0.001).minimize(total_error)

    initializer_operation = tf.global_variables_initializer()

    with tf.Session() as session:
        session.run(initializer_operation)
        _EPOCHS = 10000
        for iteration in range(_EPOCHS):
            session.run(optimizer_operation)
        slope, intercept = session.run((m, b))
        print('Slope:', slope, 'Intercept:', intercept)

if __name__ == '__main__':
    fit_line()