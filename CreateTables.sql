CREATE TABLE Linha(
    Codigo INT PRIMARY KEY NOT NULL,
    LetreiroNumerico VARCHAR(60) NOT NULL,
    ModoOperacao SMALLINT NOT NULL,
    ModoCircular BOOLEAN NOT NULL,
    Sentido SMALLINT NOT NULL,
    DescritivoPrincipal VARCHAR(50) NOT NULL,
    DescritivoSecundario VARCHAR(50) NOT NULL
);

CREATE TABLE Corredor(
	Codigo INT PRIMARY KEY NOT NULL,
	Nome VARCHAR(60) NOT NULL
);

CREATE TABLE Parada(
    Codigo INT PRIMARY KEY NOT NULL,
    Nome VARCHAR(50),
    Endereco VARCHAR(80),
    Longitude REAL NOT NULL,
    Latitude REAL NOT NULL,
    CorredorCodigo INT NOT NULL
    FOREIGN KEY(CorredorCodigo) REFERENCES Corredor(Codigo)
);

CREATE TABLE Veiculo(
	Prefixo VARCHAR(10) PRIMARY KEY NOT NULL,
	AcessoPcd BOOLEAN NOT NULL
);

CREATE TABLE LinhaParada(
	CodigoLinha INT NOT NULL,
	CodigoParada INT NOT NULL,
	PRIMARY KEY(CodigoLinha, CodigoParada),
	FOREIGN KEY(CodigoLinha) REFERENCES Linha(Codigo),
	FOREIGN KEY(CodigoParada) REFERENCES Parada(Codigo)
);

CREATE TABLE Itinerario(
	CodigoLinha INT NOT NULL,
	PrefixoVeiculo VARCHAR(10) NOT NULL,
	DataReferencia TIMESTAMP NOT NULL,
	CodigoParada INT NOT NULL,
	PrevisaoChegada TIME NOT NULL,
	PRIMARY KEY(CodigoLinha, CodigoParada, DataReferencia),
	FOREIGN KEY(CodigoLinha) REFERENCES Linha(Codigo),
	FOREIGN KEY(CodigoParada) REFERENCES Parada(Codigo),
	FOREIGN KEY(PrefixoVeiculo) REFERENCES Veiculo(Prefixo)
);
