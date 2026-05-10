using System;

namespace RedXOR
{
    class Program
    {
        static double Sigmoide(double x) => 1.0 / (1.0 + Math.Exp(-x));
        static double DSigmoide(double x) => x * (1 - x);

        static void Main(string[] args)
        {
            double[][] entradas = { new double[]{0,0}, new double[]{0,1}, new double[]{1,0}, new double[]{1,1} };
            double[][] salidas  = { new double[]{0},   new double[]{1},   new double[]{1},   new double[]{0}   };

            Random r = new Random();
            double Rand() => r.NextDouble() - 0.5;

            // pesos capa oculta con 2 entradas -> 2 neuronas ocultas
            double[,] w1 = { {Rand(), Rand()}, {Rand(), Rand()} };
            double[] b1  = { Rand(), Rand() };

            // pesos capa salida con 2 neuronas ocultas -> 1 salida
            double[] w2 = { Rand(), Rand() };
            double b2   = Rand();

            double lr    = 0.1;
            int epocas   = 0;
            double error = 1.0;

            while (error > 0.001)
            {
                error = 0;
                for (int i = 0; i < 4; i++)
                {
                    // forward
                    double h0 = Sigmoide(entradas[i][0] * w1[0,0] + entradas[i][1] * w1[1,0] + b1[0]);
                    double h1 = Sigmoide(entradas[i][0] * w1[0,1] + entradas[i][1] * w1[1,1] + b1[1]);
                    double o  = Sigmoide(h0 * w2[0] + h1 * w2[1] + b2);

                    double err = salidas[i][0] - o;
                    error += err * err;

                    // backward capa salida
                    double dO = err * DSigmoide(o);

                    // backward capa oculta
                    double dH0 = dO * w2[0] * DSigmoide(h0);
                    double dH1 = dO * w2[1] * DSigmoide(h1);

                    // actualizar pesos capa salida
                    w2[0] += lr * dO * h0;
                    w2[1] += lr * dO * h1;
                    b2    += lr * dO;

                    // actualizar pesos capa oculta
                    w1[0,0] += lr * dH0 * entradas[i][0];
                    w1[1,0] += lr * dH0 * entradas[i][1];
                    b1[0]   += lr * dH0;

                    w1[0,1] += lr * dH1 * entradas[i][0];
                    w1[1,1] += lr * dH1 * entradas[i][1];
                    b1[1]   += lr * dH1;
                }
                epocas++;
            }

            Console.WriteLine("Epocas: " + epocas);
            for (int i = 0; i < 4; i++)
            {
                double h0 = Sigmoide(entradas[i][0] * w1[0,0] + entradas[i][1] * w1[1,0] + b1[0]);
                double h1 = Sigmoide(entradas[i][0] * w1[0,1] + entradas[i][1] * w1[1,1] + b1[1]);
                double o  = Sigmoide(h0 * w2[0] + h1 * w2[1] + b2);
                int pred  = o > 0.5 ? 1 : 0;
                Console.WriteLine(entradas[i][0] + " XOR " + entradas[i][1] + " = " + salidas[i][0] + "  red = " + pred + "  (" + o.ToString("F4") + ")");
            }
            Console.ReadLine();
        }
    }
}