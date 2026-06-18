// ============================================================
// JavaScript simples do protótipo
// ============================================================
// Futuro backend:
// - Aqui podem entrar chamadas fetch() para APIs reais.
// - Exemplo: fetch('/api/specialists'), fetch('/api/payment')
// - Para o protótipo, o Flask já entrega as páginas renderizadas.
// ============================================================


// Tela de carregamento laranja.
// Ela redireciona automaticamente para a rota definida em data-next.
const splash = document.querySelector(".splash-screen");
if (splash) {
  const nextUrl = splash.dataset.next || "/login";
  setTimeout(() => {
    window.location.href = nextUrl;
  }, 1200);
}


// Cronômetro da tela de chamada.
// Em produção, isso deve ser sincronizado com o backend para evitar fraude.
// Exemplo futuro:
// - Backend salva horário de início.
// - Front consulta o status da chamada.
// - Backend calcula o valor final pelo tempo real.
const timer = document.getElementById("callTimer");
const value = document.getElementById("callValue");

if (timer && value) {
  let seconds = 0;
  const pricePerMinute = 5.00;

  setInterval(() => {
    seconds += 1;

    const h = String(Math.floor(seconds / 3600)).padStart(2, "0");
    const m = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
    const s = String(seconds % 60).padStart(2, "0");

    timer.textContent = `${h}:${m}:${s}`;

    const total = (seconds / 60) * pricePerMinute;
    value.textContent = `R$ ${total.toFixed(2)}`;
  }, 1000);
}


// Cadastro: mostra campos de especialista somente quando "Sou especialista" estiver selecionado.
const accountTypeInputs = document.querySelectorAll('input[name="account_type"]');
const specialistFields = document.querySelector(".specialist-fields");

function updateSpecialistFields() {
  if (!accountTypeInputs.length || !specialistFields) return;

  const selected = document.querySelector('input[name="account_type"]:checked');
  const isSpecialist = selected && selected.value === "specialist";

  specialistFields.style.display = isSpecialist ? "block" : "none";

  document.querySelectorAll(".tab-option").forEach((option) => {
    const input = option.querySelector('input[name="account_type"]');
    option.classList.toggle("active", input && input.checked);
  });
}

accountTypeInputs.forEach((input) => {
  input.addEventListener("change", updateSpecialistFields);
});

updateSpecialistFields();
