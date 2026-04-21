using System;

public class Program
{
	static void Program(string[] args)
	{ // {x1, x2, y}
		int[,] datos = { { 1, 1, 1 }, { 1, 0, 0 }, { 0, 1, 0 }, { 0, 0, 0 } };
		Random aleatorio = new Random();
		double[] pesos = { aleatorio.NextDouble(), aleatorio.NextDouble(), aleatorio.NextDouble(), aleatorio.NextDouble()};
		bool aprendizaje = true;
		int salidaInt;
		int epocas = 0;
		while(aprendizaje)
		{
			aprendizaje = false;
			for (int i = 0; i<4; i++)
			{
				double salidaDoub = datos[i, 0] * pesos[0] + datos[i, 1] * pesos[1] + pesos[2];
				if (salidaDoub > 0) salidaInt = 1; else slaidaInt = 0;
				if (salidaInt != datos[i,2])
				{
					pesos[0] = aleatorio.NextDouble() - aleatorio.nextDouble();
					pesos[1] = aleatorio.NextDouble() - aleatorio.nextDouble();
					pesos[2] = aleatorio.NextDouble() - aleatorio.nextDouble();
					aprendizaje = true;
                }
			}
			epocas++;
		}
		// fin de aprendizaje
		// pruebas
		for (int i = 0; i < 4; i++)
		{
			double salidaDoub = datos[i, 0] * pesos[0] + datos[i, 1] * pesos[1] + pesos[2];
			if (salidaDoub > 0) salidaInt = 1; else slaidaInt = 0;
			Console.WriteLine($"Entrada: {datos[i,0]} AND {datos[i,1]} - Salida: {salidaInt}");
        }
		Console.WriteLine($"Épocas: {epocas}");
		Console.WriteLine($"Pesos: w0= {pesos[0]}, w1= {pesos[1]}, bias= {pesos[2]}");

    }
}
