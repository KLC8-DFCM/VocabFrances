# Ideia geral

A ideia é bem simples: Temos duas "sacolas" (bags) que chamamos de outOfReview bag e reviewBag. A ideia é iniciarmos todas 
as palavras de um vocabulário (dado o nosso perfil de configuração específico) dentro da bag que não é de revisão. 

À medida que vamos acertando mais e mais palavras, eventualmente aquelas às quais já acertamos o "suficiente" (definido pelo parâmetro
de configuração minAmountTransfer) vão para a bag de revisão. À cada iteração do treinamento, temos 1 - probRessample de chance de 
escolhermos uma palavra que está na bag normal, e probRessample de chance de escolhermos uma palavra dentre as de revisão. Dado que 
uma palavra que não está na bag de revisão foi escolhida, temos chances iguais (distribuição uniforme) de escolher entre todas elas.
Dado que uma palavra da bag de revisão fora escolhida, temos uma maior chance de escolhermos (através de uma ponderação softmax) 
palavras para revisar que não vimos à muito tempo, e uma menor chance dentre as palavras que acertamos muito dentre aquelas já revisadas 
(isso ajuda a reforçar a ideia de memorização espaçada logaritimicamente). Caso erremos maxAmountRetransfer dentro da bag de revisão, considera-se 
que o usuário esqueceu-se o suficiente daquela palavra, a ponto de fazer sentido repassar para a bag normal. 

Desta forma, temos um rearranjo inteligente e dinâmico da amostragem de palavras para treino de vocabulário, com alta customização para diferentes
estilos de treino.

# Como usar

O programa é dividido na noção de separação entre perfis de configuração e palavras (vocabulário). A ideia é diferenciar seu progresso nas 
diversas áreas, e permitir a contabilidade de desempenho sob diferentes tipos de treino. 

Para adicionar um perfi de configuração, basta rodar o arquivo newSettings.py, e seguir os prompts.
Para adicionar palavras novas ao vocabulário (e consequentemente atualizar o registro em todos os perfis) basta rodar o arquivo updateVocabRepo.py e seguir os prompts.
Para utilizar o programa e treinar, basta rodar o arquivo vocab.py.

É de suma importância que os nomes e localização dos arquivos não sejam alterados, permitindo-se entretanto 
que os diversos arquivos de "estatística" (que mantém os dados de cada perfil) sejam apagados, desde que 
o usuário (para fins de consistência) também apague seu respectivo perfil no arquivo settings.csv.
