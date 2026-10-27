from services.multas_service import consultar_por_placa

def test_consultar_por_placa():
    resultado = consultar_por_placa("ABC1234")
    assert isinstance(resultado, list)