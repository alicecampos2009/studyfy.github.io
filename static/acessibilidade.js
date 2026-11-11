// ============================================================
// ACESSIBILIDADE DO STUDYFY
// Guarda as escolhas da pessoa (modo escuro, modo daltônico e tamanho da letra)
// no navegador, para valerem em todas as páginas do site.
// ============================================================

var html = document.documentElement;   // a tag <html> da página

// ----- Guardar e ler as escolhas (localStorage) -----
// O try/catch evita erro se o navegador não deixar guardar dados
function ler(nome) {
    try { return localStorage.getItem(nome); } catch (erro) { return null; }
}
function guardar(nome, valor) {
    try { localStorage.setItem(nome, valor); } catch (erro) { }
}

// ----- Escolhas atuais -----
var daltonico = ler("studyfy_daltonico") === "sim";
var tamanho = Number(ler("studyfy_tamanho")) || 100;   // tamanho da letra, em %

// Modo escuro: se a pessoa já escolheu, usa a escolha dela.
// Se nunca escolheu, segue o que o celular/computador dela usa.
var temaGuardado = ler("studyfy_tema");
var escuro;
if (temaGuardado === "escuro") {
    escuro = true;
} else if (temaGuardado === "claro") {
    escuro = false;
} else {
    escuro = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
}

// ----- Aplica as escolhas na página -----
// Modo escuro = classe "escuro" na tag <html> (o CSS troca as cores)
// Modo daltônico = classe "daltonico" na tag <html> (o CSS troca as cores)
// Tamanho da letra = muda o tamanho base, e o site todo acompanha
function aplicar() {
    html.classList.toggle("escuro", escuro);
    html.classList.toggle("daltonico", daltonico);
    html.style.fontSize = tamanho + "%";
}
aplicar();   // roda logo no começo, para a página não "piscar" com as cores normais


// ----- Botão de modo escuro / claro (fica no cabeçalho) -----
document.addEventListener("DOMContentLoaded", function () {
    var botaoTema = document.getElementById("tema-botao");
    var iconeTema = botaoTema.querySelector("i");
    var textoTema = botaoTema.querySelector("span");

    // O botão mostra o que vai acontecer se clicar: no escuro, oferece o claro (e vice-versa)
    function atualizarBotaoTema() {
        iconeTema.className = escuro ? "fa-solid fa-sun" : "fa-solid fa-moon";
        textoTema.textContent = escuro ? "Modo claro" : "Modo escuro";
    }

    botaoTema.addEventListener("click", function () {
        escuro = !escuro;
        aplicar();
        guardar("studyfy_tema", escuro ? "escuro" : "claro");
        atualizarBotaoTema();
    });

    atualizarBotaoTema();
});


// ----- Botões do painel de acessibilidade (só funcionam depois que a página carregou) -----
document.addEventListener("DOMContentLoaded", function () {

    var botaoAbrir = document.getElementById("acess-abrir");
    var painel = document.getElementById("acess-painel");
    var botaoDaltonico = document.getElementById("acess-daltonico");
    var textoDaltonico = document.getElementById("acess-daltonico-texto");
    var textoTamanho = document.getElementById("acess-tamanho");
    var botaoMais = document.getElementById("acess-mais");
    var botaoMenos = document.getElementById("acess-menos");
    var botaoRestaurar = document.getElementById("acess-restaurar");

    // Atualiza os textos do painel de acordo com as escolhas
    function atualizarPainel() {
        botaoDaltonico.setAttribute("aria-pressed", daltonico);
        textoDaltonico.textContent = daltonico ? "Ativado" : "Desativado";
        textoTamanho.textContent = tamanho + "%";
        botaoMais.disabled = tamanho >= 140;    // limite máximo
        botaoMenos.disabled = tamanho <= 80;    // limite mínimo
    }

    // Aplica, guarda e atualiza o painel (usado depois de qualquer clique)
    function salvarTudo() {
        aplicar();
        guardar("studyfy_daltonico", daltonico ? "sim" : "nao");
        guardar("studyfy_tamanho", tamanho);
        atualizarPainel();
    }

    // Abre e fecha o painel
    function mostrarPainel(mostrar) {
        painel.hidden = !mostrar;
        botaoAbrir.setAttribute("aria-expanded", mostrar);
    }

    botaoAbrir.addEventListener("click", function () {
        mostrarPainel(painel.hidden);   // se está escondido, mostra (e vice-versa)
    });

    // Tecla Esc fecha o painel
    document.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape" && !painel.hidden) {
            mostrarPainel(false);
            botaoAbrir.focus();
        }
    });

    // Liga e desliga o modo daltônico
    botaoDaltonico.addEventListener("click", function () {
        daltonico = !daltonico;
        salvarTudo();
    });

    // Aumenta e diminui a letra (de 10 em 10%)
    botaoMais.addEventListener("click", function () {
        tamanho = tamanho + 10;
        salvarTudo();
    });
    botaoMenos.addEventListener("click", function () {
        tamanho = tamanho - 10;
        salvarTudo();
    });

    // Volta tudo ao normal
    botaoRestaurar.addEventListener("click", function () {
        daltonico = false;
        tamanho = 100;
        salvarTudo();
    });

    atualizarPainel();   // deixa o painel certo ao carregar a página
});
