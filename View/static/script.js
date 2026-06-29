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
// No protótipo, o tempo é enviado para a tela de pagamento via query string.
const timer = document.getElementById("callTimer");
const value = document.getElementById("callValue");
const callScreen = document.querySelector(".call-screen");
const endCallLink = document.getElementById("endCallLink");

if (timer && value) {
  let seconds = 0;
  const rawPrice = callScreen?.dataset.pricePerMinute || "0";
  const pricePerMinute = Number(String(rawPrice).replace(",", ".")) || 0;
  const paymentUrl = callScreen?.dataset.paymentUrl || endCallLink?.getAttribute("href")?.split("?")[0] || "";

  setInterval(() => {
    seconds += 1;

    const h = String(Math.floor(seconds / 3600)).padStart(2, "0");
    const m = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
    const s = String(seconds % 60).padStart(2, "0");

    timer.textContent = `${h}:${m}:${s}`;

    const total = (seconds / 60) * pricePerMinute;
    value.textContent = total.toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL"
    });

    if (endCallLink && paymentUrl) {
      endCallLink.href = `${paymentUrl}?tempo=${Math.max(seconds, 1)}`;
    }
  }, 1000);
}


// Seleção visual da forma de pagamento.
document.querySelectorAll('.payment-option input[name="payment_method"]').forEach((input) => {
  input.addEventListener("change", () => {
    document.querySelectorAll(".payment-option").forEach((option) => {
      option.classList.remove("active");
    });

    input.closest(".payment-option")?.classList.add("active");
  });
});



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


// Modal complementar por perfil: cliente paga, especialista recebe.
const flowModals = document.querySelectorAll(".flow-modal-backdrop");

flowModals.forEach((modal) => {
  modal.querySelectorAll("[data-close-modal]").forEach((button) => {
    button.addEventListener("click", () => {
      modal.classList.add("is-hidden");
    });
  });
});

// Dropdown customizado para selects com data-apple-select
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("select[data-apple-select]").forEach((select) => {
    if (select.dataset.appleSelectReady === "true") return;

    select.dataset.appleSelectReady = "true";
    select.classList.add("apple-select-native");

    const wrapper = document.createElement("div");
    wrapper.className = "apple-select-wrapper";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "apple-select-button";
    button.textContent = select.options[select.selectedIndex]?.text || "Selecione";

    const menu = document.createElement("div");
    menu.className = "apple-select-menu";

    Array.from(select.options).forEach((option) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "apple-select-option";
      item.textContent = option.text;
      item.dataset.value = option.value;

      if (option.selected) {
        item.classList.add("active");
      }

      item.addEventListener("click", () => {
        select.value = option.value;
        button.textContent = option.text;

        menu.querySelectorAll(".apple-select-option").forEach((el) => {
          el.classList.remove("active");
        });

        item.classList.add("active");
        wrapper.classList.remove("open");

        select.dispatchEvent(new Event("change", { bubbles: true }));
      });

      menu.appendChild(item);
    });

    select.parentNode.insertBefore(wrapper, select);
    wrapper.appendChild(select);
    wrapper.appendChild(button);
    wrapper.appendChild(menu);

    button.addEventListener("click", () => {
      document.querySelectorAll(".apple-select-wrapper.open").forEach((openWrapper) => {
        if (openWrapper !== wrapper) {
          openWrapper.classList.remove("open");
        }
      });

      wrapper.classList.toggle("open");
    });
  });

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".apple-select-wrapper")) {
      document.querySelectorAll(".apple-select-wrapper.open").forEach((wrapper) => {
        wrapper.classList.remove("open");
      });
    }
  });
});

// Modais internos das páginas do especialista
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-open-specialist-modal]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();

      const modalName = button.getAttribute("data-open-specialist-modal");
      const modal = document.querySelector(`[data-specialist-modal="${modalName}"]`);

      if (modal) {
        modal.classList.add("is-open");
      }
    });
  });

  document.querySelectorAll("[data-close-specialist-modal]").forEach((button) => {
    button.addEventListener("click", () => {
      button.closest(".specialist-modal-backdrop")?.classList.remove("is-open");
    });
  });

  document.querySelectorAll(".specialist-modal-backdrop").forEach((backdrop) => {
    backdrop.addEventListener("click", (event) => {
      if (event.target === backdrop) {
        backdrop.classList.remove("is-open");
      }
    });
  });
});

// Abas dentro dos modais do especialista
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-specialist-tab]").forEach((tab) => {
    tab.addEventListener("click", () => {
      const modal = tab.closest(".specialist-modal");
      const target = tab.getAttribute("data-specialist-tab");

      if (!modal || !target) return;

      modal.querySelectorAll("[data-specialist-tab]").forEach((item) => {
        item.classList.remove("active");
      });

      modal.querySelectorAll("[data-specialist-tab-panel]").forEach((panel) => {
        panel.classList.remove("active");
      });

      tab.classList.add("active");

      const targetPanel = modal.querySelector(`[data-specialist-tab-panel="${target}"]`);
      if (targetPanel) {
        targetPanel.classList.add("active");
      }
    });
  });
});

// Seleção de plano pelos cards no modal de assinatura
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-plan-option]").forEach((card) => {
    card.addEventListener("click", () => {
      const modal = card.closest(".specialist-modal");
      const selectedPlan = card.getAttribute("data-plan-option");
      const hiddenInput = modal?.querySelector("#plano_desejado");

      if (!modal || !selectedPlan || !hiddenInput) return;

      modal.querySelectorAll("[data-plan-option]").forEach((item) => {
        item.classList.remove("active");
      });

      card.classList.add("active");
      hiddenInput.value = selectedPlan;
    });
  });
});

// Editor de tags do perfil especialista
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-tag-editor]").forEach((editor) => {
    const list = editor.querySelector("[data-tag-list]");
    const input = editor.querySelector("[data-tag-input]");
    const addButton = editor.querySelector("[data-add-tag]");
    const hidden = editor.querySelector("[data-tags-hidden]");

    if (!list || !input || !addButton || !hidden) return;

    let tags = hidden.value
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean);

    function syncTags() {
      hidden.value = tags.join(", ");
    }

    function renderTags() {
      list.innerHTML = "";

      tags.forEach((tag, index) => {
        const chip = document.createElement("span");
        chip.className = "tag-chip-edit";
        chip.textContent = tag;

        const remove = document.createElement("button");
        remove.type = "button";
        remove.textContent = "×";
        remove.setAttribute("aria-label", `Remover ${tag}`);

        remove.addEventListener("click", () => {
          tags.splice(index, 1);
          syncTags();
          renderTags();
        });

        chip.appendChild(remove);
        list.appendChild(chip);
      });

      syncTags();
    }

    function addTag() {
      const value = input.value.trim();

      if (!value) return;

      const exists = tags.some((tag) => tag.toLowerCase() === value.toLowerCase());

      if (!exists) {
        tags.push(value);
      }

      input.value = "";
      syncTags();
      renderTags();
    }

    addButton.addEventListener("click", addTag);

    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        addTag();
      }
    });

    renderTags();
  });
});

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".profile-photo-auto-form input[type='file']").forEach((input) => {
    input.addEventListener("change", () => {
      if (input.files && input.files.length > 0) {
        input.closest("form").submit();
      }
    });
  });
});

/* Foto do perfil - fluxo final único */
document.addEventListener("DOMContentLoaded", () => {
  const modal = document.querySelector("[data-profile-photo-modal]");
  if (!modal || modal.dataset.photoReady === "true") return;

  modal.dataset.photoReady = "true";

  const title = modal.querySelector("[data-photo-modal-title]");
  const subtitle = modal.querySelector("[data-photo-modal-subtitle]");

  const titles = {
    view: ["Foto do perfil", "Veja a foto atual ou envie uma nova imagem para o perfil público."],
    update: ["Atualizar foto", "Escolha uma imagem, ajuste o enquadramento e salve."],
    delete: ["Excluir foto", "A exclusão definitiva será conectada ao backend depois."]
  };

  function setPanel(panelName) {
    modal.querySelectorAll("[data-photo-panel]").forEach((panel) => {
      panel.classList.toggle("active", panel.dataset.photoPanel === panelName);
    });

    if (title && subtitle && titles[panelName]) {
      title.textContent = titles[panelName][0];
      subtitle.textContent = titles[panelName][1];
    }
  }

  document.querySelectorAll("[data-open-profile-photo-modal]").forEach((button) => {
    button.addEventListener("click", () => {
      modal.classList.add("active");
      document.body.classList.add("modal-open");
      setPanel("view");
    });
  });

  modal.querySelectorAll("[data-close-profile-photo-modal]").forEach((button) => {
    button.addEventListener("click", () => {
      modal.classList.remove("active");
      document.body.classList.remove("modal-open");
      setPanel("view");
    });
  });

  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.classList.remove("active");
      document.body.classList.remove("modal-open");
      setPanel("view");
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal.classList.contains("active")) {
      modal.classList.remove("active");
      document.body.classList.remove("modal-open");
      setPanel("view");
    }
  });

  modal.querySelectorAll("[data-photo-panel-button]").forEach((button) => {
    button.addEventListener("click", () => {
      setPanel(button.dataset.photoPanelButton);
    });
  });

  const form = modal.querySelector("[data-photo-crop-form]");
  const input = modal.querySelector("[data-photo-crop-input]");
  const preview = modal.querySelector("[data-photo-crop-preview]");
  const zoom = modal.querySelector("[data-photo-zoom]");
  const positionY = modal.querySelector("[data-photo-position-y]");
  const saveButton = modal.querySelector("[data-photo-save-crop]");

  if (!form || !input || !preview || !zoom || !positionY || !saveButton) return;

  let selectedFile = null;
  let previewImage = preview.querySelector("img");
  let previewNaturalWidth = previewImage ? previewImage.naturalWidth || 1 : 1;
  let previewNaturalHeight = previewImage ? previewImage.naturalHeight || 1 : 1;

  saveButton.disabled = true;
  saveButton.classList.add("disabled");

  function getPreviewSize() {
    const rect = preview.getBoundingClientRect();
    return {
      width: rect.width || 120,
      height: rect.height || 120
    };
  }

  function updateVerticalLimits() {
    if (!previewImage || !previewNaturalWidth || !previewNaturalHeight) return;

    const container = getPreviewSize();
    const currentZoom = Number(zoom.value);

    const baseScale = Math.max(
      container.width / previewNaturalWidth,
      container.height / previewNaturalHeight
    );

    const renderedHeight = previewNaturalHeight * baseScale * currentZoom;
    const maxOffset = Math.max(0, (renderedHeight - container.height) / 2);

    positionY.min = String(Math.round(-maxOffset));
    positionY.max = String(Math.round(maxOffset));

    let currentValue = Number(positionY.value);
    if (currentValue < -maxOffset) currentValue = -maxOffset;
    if (currentValue > maxOffset) currentValue = maxOffset;

    positionY.value = String(Math.round(currentValue));
  }

  function applyPreviewTransform() {
    if (!previewImage) return;

    updateVerticalLimits();

    previewImage.style.transform = `translateY(${Number(positionY.value)}px) scale(${Number(zoom.value)})`;
  }

  input.addEventListener("change", () => {
    if (!input.files || input.files.length === 0) return;

    selectedFile = input.files[0];
    const url = URL.createObjectURL(selectedFile);

    preview.innerHTML = "";

    previewImage = document.createElement("img");
    previewImage.src = url;
    previewImage.alt = "Prévia da foto";
    preview.appendChild(previewImage);

    previewImage.onload = () => {
      previewNaturalWidth = previewImage.naturalWidth || 1;
      previewNaturalHeight = previewImage.naturalHeight || 1;

      zoom.value = "1";
      positionY.value = "0";

      saveButton.disabled = false;
      saveButton.classList.remove("disabled");

      applyPreviewTransform();
    };
  });

  zoom.addEventListener("input", applyPreviewTransform);
  positionY.addEventListener("input", applyPreviewTransform);

  modal.querySelectorAll("[data-photo-range-step]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = button.dataset.photoRangeStep;
      const step = Number(button.dataset.step || 0);

      if (target === "zoom") {
        const next = Math.min(
          Number(zoom.max),
          Math.max(Number(zoom.min), Number(zoom.value) + step)
        );

        zoom.value = next.toFixed(2);
        applyPreviewTransform();
      }

      if (target === "vertical") {
        const next = Math.min(
          Number(positionY.max),
          Math.max(Number(positionY.min), Number(positionY.value) + step)
        );

        positionY.value = String(Math.round(next));
        applyPreviewTransform();
      }
    });
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!selectedFile || !previewImage) return;

    const canvas = document.createElement("canvas");
    const size = 600;

    canvas.width = size;
    canvas.height = size;

    const ctx = canvas.getContext("2d");
    const img = new Image();

    img.onload = () => {
      const currentZoom = Number(zoom.value);
      const baseScale = Math.max(size / img.width, size / img.height);
      const finalScale = baseScale * currentZoom;

      const drawWidth = img.width * finalScale;
      const drawHeight = img.height * finalScale;

      const maxCanvasOffset = Math.max(0, (drawHeight - size) / 2);
      const requestedOffset = Number(positionY.value) * (size / getPreviewSize().height);
      const safeOffset = Math.min(maxCanvasOffset, Math.max(-maxCanvasOffset, requestedOffset));

      const dx = (size - drawWidth) / 2;
      const dy = (size - drawHeight) / 2 + safeOffset;

      ctx.fillStyle = "#f8fafc";
      ctx.fillRect(0, 0, size, size);
      ctx.drawImage(img, dx, dy, drawWidth, drawHeight);

      canvas.toBlob((blob) => {
        if (!blob) return;

        const formData = new FormData();
        formData.append("foto_perfil", blob, "foto_perfil.png");

        fetch("/especialista/perfil/foto", {
          method: "POST",
          body: formData
        }).then(() => {
          window.location.href = "/especialista/perfil";
        });
      }, "image/png", 0.92);
    };

    img.src = URL.createObjectURL(selectedFile);
  });
});



// Fluxo fake de pagamento.
// Simula retorno de operadora para cartão e confirmação de PIX.
const fakePaymentForm = document.getElementById("fakePaymentForm");
const gatewayStatus = document.getElementById("gatewayStatus");
const cardPaymentModal = document.getElementById("cardPaymentModal");
const cardPaymentStatus = document.getElementById("cardPaymentStatus");
const pixPaymentModal = document.getElementById("pixPaymentModal");
const approvePixPayment = document.getElementById("approvePixPayment");
const cancelPixPayment = document.getElementById("cancelPixPayment");
const pixCountdown = document.getElementById("pixCountdown");
const pixPreview = document.getElementById("pixPreview");

function getSelectedPaymentMethod() {
  return document.querySelector('input[name="payment_method"]:checked')?.value || "cartao";
}

function submitApprovedPayment() {
  if (!fakePaymentForm || !gatewayStatus) return;

  gatewayStatus.value = "approved";
  fakePaymentForm.dataset.confirmed = "true";
  fakePaymentForm.submit();
}

function openPaymentModal(modal) {
  modal?.classList.remove("is-hidden");
}

function closePaymentModal(modal) {
  modal?.classList.add("is-hidden");
}

function startPixCountdown() {
  if (!pixCountdown) return;

  let seconds = 300;

  const interval = setInterval(() => {
    seconds -= 1;

    if (!pixPaymentModal || pixPaymentModal.classList.contains("is-hidden")) {
      clearInterval(interval);
      return;
    }

    const minutes = String(Math.floor(seconds / 60)).padStart(2, "0");
    const secs = String(seconds % 60).padStart(2, "0");

    pixCountdown.textContent = `${minutes}:${secs}`;

    if (seconds <= 0) {
      clearInterval(interval);
      pixCountdown.textContent = "Expirado";
    }
  }, 1000);
}

if (fakePaymentForm) {
  fakePaymentForm.addEventListener("submit", (event) => {
    if (fakePaymentForm.dataset.confirmed === "true") return;

    event.preventDefault();

    const method = getSelectedPaymentMethod();

    if (method === "cartao") {
      openPaymentModal(cardPaymentModal);

      let seconds = 30;

      if (cardPaymentStatus) {
        cardPaymentStatus.textContent = `Autorizando com a operadora fake... aprovação em ${seconds}s`;
      }

      const interval = setInterval(() => {
        seconds -= 1;

        if (cardPaymentStatus) {
          cardPaymentStatus.textContent = `Autorizando com a operadora fake... aprovação em ${seconds}s`;
        }

        if (seconds <= 0) {
          clearInterval(interval);

          if (cardPaymentStatus) {
            cardPaymentStatus.textContent = "Pagamento aprovado pela operadora fake.";
          }

          setTimeout(() => {
            submitApprovedPayment();
          }, 900);
        }
      }, 1000);

      return;
    }

    if (method === "pix") {
      openPaymentModal(pixPaymentModal);
      startPixCountdown();
    }
  });
}

approvePixPayment?.addEventListener("click", () => {
  submitApprovedPayment();
});

cancelPixPayment?.addEventListener("click", () => {
  closePaymentModal(pixPaymentModal);
});

document.querySelectorAll('input[name="payment_method"]').forEach((input) => {
  input.addEventListener("change", () => {
    const method = getSelectedPaymentMethod();

    if (pixPreview) {
      pixPreview.classList.toggle("is-visible", method === "pix");
    }
  });
});



// Avaliação: habilita envio somente após selecionar uma estrela.
// Comentário é opcional.
const reviewSubmitButton = document.getElementById("reviewSubmitButton");
const reviewRatingInputs = document.querySelectorAll('.star-input input[name="rating"]');

function updateReviewSubmitState() {
  if (!reviewSubmitButton || !reviewRatingInputs.length) return;

  const hasRating = Boolean(document.querySelector('.star-input input[name="rating"]:checked'));

  reviewSubmitButton.disabled = !hasRating;
  reviewSubmitButton.classList.toggle("disabled-look", !hasRating);
}

reviewRatingInputs.forEach((input) => {
  input.addEventListener("change", updateReviewSubmitState);
});

updateReviewSubmitState();



// Controles fake da chamada.
const muteCallButton = document.getElementById("muteCallButton");
const videoCallButton = document.getElementById("videoCallButton");
const videoConfirmModal = document.getElementById("videoConfirmModal");
const confirmVideoButton = document.getElementById("confirmVideoButton");
const cancelVideoButton = document.getElementById("cancelVideoButton");

muteCallButton?.addEventListener("click", () => {
  const isMuted = muteCallButton.classList.toggle("is-muted");
  const label = muteCallButton.querySelector("small");

  if (label) {
    label.textContent = isMuted ? "Microfone mudo" : "Microfone ativo";
  }
});

videoCallButton?.addEventListener("click", () => {
  videoConfirmModal?.classList.remove("is-hidden");
});

cancelVideoButton?.addEventListener("click", () => {
  videoConfirmModal?.classList.add("is-hidden");
});

confirmVideoButton?.addEventListener("click", () => {
  videoConfirmModal?.classList.add("is-hidden");
  videoCallButton?.classList.add("is-active");

  const label = videoCallButton?.querySelector("small");
  if (label) {
    label.textContent = "Câmera ligada";
  }
});



// CALENDARIO_MENSAL_DISPONIBILIDADE
(() => {
  const openScheduleModal = document.getElementById("openScheduleModal");
  const openScheduleModalPrimary = document.getElementById("openScheduleModalPrimary");
  const closeScheduleModal = document.getElementById("closeScheduleModal");
  const scheduleModal = document.getElementById("scheduleModal");
  const scheduleSuccess = document.getElementById("scheduleSuccess");
  const scheduleSlotPanel = document.getElementById("scheduleSlotPanel");
  const confirmScheduleButton = document.getElementById("confirmScheduleButton");
  const scheduleCalendar = document.getElementById("scheduleCalendar");
  const scheduleMonthTitle = document.getElementById("scheduleMonthTitle");
  const prevScheduleMonth = document.getElementById("prevScheduleMonth");
  const nextScheduleMonth = document.getElementById("nextScheduleMonth");

  if (!scheduleModal || !scheduleSlotPanel || !scheduleCalendar || !scheduleMonthTitle) return;

  const specialistId = scheduleModal?.dataset?.specialistId || "";

  const weekdays = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];
  const monthNames = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
  ];

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const maxDate = new Date(today);
  maxDate.setDate(maxDate.getDate() + 30);

  let currentMonthDate = new Date(today.getFullYear(), today.getMonth(), 1);
  let selectedDayText = "";
  let selectedSlot = "";
  let firstCouponAvailable = false;
  let couponApplied = "";

  function parseDayDate(date) {
    const copy = new Date(date);
    copy.setHours(0, 0, 0, 0);
    return copy;
  }

  function isDateAvailable(date) {
    const parsed = parseDayDate(date);
    return parsed >= today && parsed <= maxDate;
  }

  function buildSlots(date) {
    const day = date.getDate();
    const baseSlots = ["09:00", "11:00", "15:00", "18:30", "20:00"];

    return baseSlots.map((slot, index) => {
      const reserved = (day + index) % 4 === 0;
      return {
        hour: slot,
        reserved
      };
    });
  }

  async function carregarStatusCupom() {
    firstCouponAvailable = false;
    couponApplied = "";

    if (!specialistId) return;

    try {
      const response = await fetch(`/api/cupom-primeiro-atendimento/status?especialista_id=${encodeURIComponent(specialistId)}`);
      const data = await response.json();

      firstCouponAvailable = Boolean(response.ok && data.ok && data.disponivel);
    } catch {
      firstCouponAvailable = false;
    }
  }

  function updateMonthButtons() {
    const previousMonth = new Date(currentMonthDate.getFullYear(), currentMonthDate.getMonth() - 1, 1);
    const nextMonth = new Date(currentMonthDate.getFullYear(), currentMonthDate.getMonth() + 1, 1);

    const minMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    const maxMonth = new Date(maxDate.getFullYear(), maxDate.getMonth(), 1);

    if (prevScheduleMonth) {
      prevScheduleMonth.disabled = previousMonth < minMonth;
    }

    if (nextScheduleMonth) {
      nextScheduleMonth.disabled = nextMonth > maxMonth;
    }
  }

  function renderCalendar() {
    const year = currentMonthDate.getFullYear();
    const month = currentMonthDate.getMonth();
    const totalDays = new Date(year, month + 1, 0).getDate();

    scheduleMonthTitle.textContent = `${monthNames[month]} ${year}`;
    scheduleCalendar.innerHTML = "";

    for (let day = 1; day <= totalDays; day++) {
      const date = new Date(year, month, day);
      const available = isDateAvailable(date);
      const isToday = parseDayDate(date).getTime() === today.getTime();

      const button = document.createElement("button");
      button.type = "button";
      button.className = `schedule-day ${isToday ? "today" : ""} ${available ? "" : "locked"}`;
      button.dataset.day = String(day);
      button.dataset.weekday = weekdays[date.getDay()];
      button.dataset.fullDate = date.toISOString();

      if (!available) {
        button.disabled = true;
      }

      button.innerHTML = `
        <small>${weekdays[date.getDay()]}</small>
        <strong>${day}</strong>
      `;

      button.addEventListener("click", () => montarHorarios(button, date));
      scheduleCalendar.appendChild(button);
    }

    updateMonthButtons();
  }

  function resetarBotaoConfirmacao() {
    if (!confirmScheduleButton) return;

    confirmScheduleButton.disabled = true;
    confirmScheduleButton.classList.remove("is-ready");
    confirmScheduleButton.textContent = "Solicitar atendimento";
  }

  function resetarPainel() {
    selectedDayText = "";
    selectedSlot = "";
    couponApplied = "";

    document.querySelectorAll(".schedule-day").forEach((item) => {
      item.classList.remove("active");
    });

    scheduleSlotPanel.innerHTML = `
      <div class="schedule-empty-line">
        <strong>Selecione um dia disponível:</strong>
        <span>os horários liberados aparecerão aqui.</span>
      </div>
    `;

    scheduleSuccess?.classList.add("is-hidden");
    resetarBotaoConfirmacao();
  }

  async function abrirModal() {
    await carregarStatusCupom();

    currentMonthDate = new Date(today.getFullYear(), today.getMonth(), 1);
    renderCalendar();
    resetarPainel();
    scheduleModal.classList.remove("is-hidden");
  }

  function fecharModal() {
    scheduleModal.classList.add("is-hidden");
  }

  function renderCouponArea() {
    if (firstCouponAvailable) {
      return `
        <div class="coupon-area is-hidden" id="couponArea">
          <label for="couponInput">Cupom de primeiro atendimento</label>
          <div class="coupon-line">
            <input id="couponInput" type="text" value="PRIMEIRA5" placeholder="PRIMEIRA5">
            <button type="button" id="applyCouponButton">Aplicar</button>
          </div>
          <small id="couponFeedback">
            Use PRIMEIRA5 para 5% de desconto na primeiro atendimento no Tele-Severino. Depois de usar, o cupom fica indisponível.
          </small>
          <div class="specialist-coupon-hint">
            Cupons do especialista poderão aparecer aqui quando o profissional liberar campanhas no plano dele.
          </div>
        </div>
      `;
    }

    return `
      <div class="coupon-area coupon-area-used is-hidden" id="couponArea">
        <strong>Cupom de primeiro atendimento já utilizado</strong>
        <small>
          O cupom PRIMEIRA5 só pode ser usado uma vez no seu histórico.
        </small>
      </div>
    `;
  }

  function montarHorarios(button, date) {
    const jaSelecionado = button.classList.contains("active");

    if (jaSelecionado) {
      resetarPainel();
      return;
    }

    const day = button.dataset.day;
    const weekday = button.dataset.weekday;
    const slots = buildSlots(date);

    selectedDayText = `${weekday}, dia ${day}`;
    selectedSlot = "";
    couponApplied = "";

    document.querySelectorAll(".schedule-day").forEach((item) => {
      item.classList.remove("active");
    });

    button.classList.add("active");
    scheduleSuccess?.classList.add("is-hidden");
    resetarBotaoConfirmacao();

    scheduleSlotPanel.classList.add("is-changing");

    setTimeout(() => {
      const slotButtons = slots.map((slot) => {
        const status = slot.reserved ? "Reservado" : "Livre";
        const classe = slot.reserved ? "reserved" : "free";
        const disabled = slot.reserved ? "disabled" : "";

        return `
          <button type="button" class="schedule-slot ${classe}" ${disabled} data-slot="${slot.hour}">
            <strong>${slot.hour}</strong>
            <small>${status}</small>
          </button>
        `;
      }).join("");

      scheduleSlotPanel.innerHTML = `
        <strong>${selectedDayText}</strong>
        <p>Escolha um horário livre para solicitar sua videochamada.</p>

        <div class="schedule-slots">
          ${slotButtons}
        </div>

        ${renderCouponArea()}
      `;

      scheduleSlotPanel.classList.remove("is-changing");

      scheduleSlotPanel.querySelectorAll(".schedule-slot.free").forEach((slotButton) => {
        slotButton.addEventListener("click", () => {
          scheduleSlotPanel.querySelectorAll(".schedule-slot").forEach((item) => {
            item.classList.remove("active");
          });

          slotButton.classList.add("active");
          selectedSlot = slotButton.dataset.slot || "";

          const couponArea = document.getElementById("couponArea");
          couponArea?.classList.remove("is-hidden");

          scheduleSuccess?.classList.add("is-hidden");

          if (confirmScheduleButton) {
            confirmScheduleButton.disabled = false;
            confirmScheduleButton.classList.add("is-ready");
            confirmScheduleButton.textContent = "Solicitar atendimento";
          }
        });
      });

      const applyCouponButton = document.getElementById("applyCouponButton");
      const couponInput = document.getElementById("couponInput");
      const couponFeedback = document.getElementById("couponFeedback");

      applyCouponButton?.addEventListener("click", () => {
        const codigo = String(couponInput?.value || "").trim().toUpperCase();

        if (!codigo) {
          couponApplied = "";
          couponFeedback.textContent = "Digite PRIMEIRA5 para aplicar o cupom de primeiro atendimento.";
          couponFeedback.className = "coupon-feedback warning";
          return;
        }

        if (codigo !== "PRIMEIRA5") {
          couponApplied = "";
          couponFeedback.textContent = "Cupom inválido. Para este protótipo, use PRIMEIRA5.";
          couponFeedback.className = "coupon-feedback error";
          return;
        }

        if (!firstCouponAvailable) {
          couponApplied = "";
          couponFeedback.textContent = "Você já utilizou o cupom PRIMEIRA5 no seu primeiro atendimento.";
          couponFeedback.className = "coupon-feedback error";
          return;
        }

        couponApplied = "PRIMEIRA5";
        couponFeedback.textContent = "Cupom PRIMEIRA5 aplicado: 5% de desconto no primeiro atendimento no Tele-Severino.";
        couponFeedback.className = "coupon-feedback success";
      });
    }, 180);
  }

  function mostrarPopupSolicitacao() {
    const popup = document.createElement("div");
    popup.className = "schedule-success-popup";
    popup.innerHTML = `
      <div>
        <strong>Solicitação enviada com sucesso</strong>
        <p>
          Agora é necessário aguardar o retorno do especialista.
          Ele poderá aceitar ou recusar sua solicitação de atendimento.
        </p>
        <button type="button">Entendi</button>
      </div>
    `;

    document.body.appendChild(popup);

    popup.querySelector("button")?.addEventListener("click", () => {
      popup.remove();
    });

    setTimeout(() => {
      popup.classList.add("is-visible");
    }, 50);
  }

  openScheduleModal?.addEventListener("click", abrirModal);
  openScheduleModalPrimary?.addEventListener("click", abrirModal);
  closeScheduleModal?.addEventListener("click", fecharModal);

  prevScheduleMonth?.addEventListener("click", () => {
    currentMonthDate = new Date(currentMonthDate.getFullYear(), currentMonthDate.getMonth() - 1, 1);
    renderCalendar();
    resetarPainel();
  });

  nextScheduleMonth?.addEventListener("click", () => {
    currentMonthDate = new Date(currentMonthDate.getFullYear(), currentMonthDate.getMonth() + 1, 1);
    renderCalendar();
    resetarPainel();
  });

  confirmScheduleButton?.addEventListener("click", async () => {
    if (confirmScheduleButton.disabled || !selectedSlot) return;

    confirmScheduleButton.disabled = true;
    confirmScheduleButton.textContent = "Enviando...";

    try {
      const response = await fetch("/api/solicitacoes-atendimento", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          id_especialista: specialistId,
          dia_label: selectedDayText,
          horario: selectedSlot,
          cupom_codigo: couponApplied
        })
      });

      const data = await response.json();

      if (!response.ok || !data.ok) {
        throw new Error(data.erro || "Não foi possível enviar a solicitação.");
      }

      if (data.cupom_codigo === "PRIMEIRA5") {
        firstCouponAvailable = false;
        couponApplied = "";
      }

      if (scheduleSuccess) {
        scheduleSuccess.classList.remove("is-hidden");
        scheduleSuccess.innerHTML = `
          <strong>Solicitação enviada</strong>
          <span>
            Pedido registrado para ${selectedDayText}, às ${selectedSlot}.
            ${data.cupom_codigo === "PRIMEIRA5" ? "Cupom PRIMEIRA5 aplicado nesta solicitação. " : ""}
            Aguarde o aceite ou recusa do especialista.
          </span>
        `;
      }

      confirmScheduleButton.textContent = "Solicitação enviada";
      confirmScheduleButton.classList.remove("is-ready");
      mostrarPopupSolicitacao();
    } catch (erro) {
      if (scheduleSuccess) {
        scheduleSuccess.classList.remove("is-hidden");
        scheduleSuccess.innerHTML = `
          <strong>Não foi possível enviar</strong>
          <span>${erro.message}</span>
        `;
      }

      confirmScheduleButton.disabled = false;
      confirmScheduleButton.textContent = "Tentar novamente";
      confirmScheduleButton.classList.add("is-ready");
    }
  });
})();



// LIVE_SPECIALIST_SEARCH_FILTER
(() => {
  const searchInput = document.getElementById("specialistLiveSearch");
  const clearButton = document.getElementById("clearSpecialistSearch");
  const filterTabs = document.getElementById("priceFilterTabs");
  const counter = document.getElementById("specialistResultCounter");
  const list = document.querySelector(".client-specialists-list");

  if (!searchInput || !list) return;

  const cards = Array.from(document.querySelectorAll(".client-specialist-card"));

  function normalizeText(value) {
    return String(value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim();
  }

  function getSelectedSort() {
    const active = filterTabs?.querySelector("button.active");
    return active?.dataset.sort || "";
  }

  function updateCounter(total) {
    if (!counter) return;

    if (total === 0) {
      counter.textContent = "Nenhum especialista encontrado";
      return;
    }

    if (total === 1) {
      counter.textContent = "1 especialista encontrado";
      return;
    }

    counter.textContent = `${total} especialistas encontrados`;
  }

  function applySearchAndSort() {
    const term = normalizeText(searchInput.value);
    const sort = getSelectedSort();

    let visibleCards = cards.filter((card) => {
      const searchable = normalizeText(card.dataset.search);
      return !term || searchable.includes(term);
    });

    if (sort === "menor_preco") {
      visibleCards.sort((a, b) => {
        return Number(a.dataset.price || 0) - Number(b.dataset.price || 0);
      });
    }

    if (sort === "maior_preco") {
      visibleCards.sort((a, b) => {
        return Number(b.dataset.price || 0) - Number(a.dataset.price || 0);
      });
    }

    cards.forEach((card) => {
      card.classList.add("is-hidden-by-search");
    });

    visibleCards.forEach((card) => {
      card.classList.remove("is-hidden-by-search");
      list.appendChild(card);
    });

    updateCounter(visibleCards.length);
  }

  searchInput.addEventListener("input", applySearchAndSort);

  clearButton?.addEventListener("click", () => {
    const hasCategory = clearButton.dataset.hasCategory === "true";
    const clearUrl = clearButton.dataset.clearUrl || "/especialistas";

    if (hasCategory) {
      window.location.href = clearUrl;
      return;
    }

    searchInput.value = "";

    filterTabs?.querySelectorAll("button").forEach((button) => {
      button.classList.toggle("active", button.dataset.sort === "");
    });

    applySearchAndSort();
    searchInput.focus();
  });

  filterTabs?.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      filterTabs.querySelectorAll("button").forEach((item) => {
        item.classList.remove("active");
      });

      button.classList.add("active");
      applySearchAndSort();
    });
  });

  applySearchAndSort();
})();


// ONLINE OFFLINE FILTER EXTENSION
document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("specialistLiveSearch");
  const clearButton = document.getElementById("clearSpecialistSearch");
  const priceTabs = document.getElementById("priceFilterTabs");
  const statusTabs = document.getElementById("statusFilterTabs");
  const counter = document.getElementById("specialistResultCounter");

  const cards = Array.from(document.querySelectorAll(".client-specialist-card"));

  if (!cards.length || !statusTabs) {
    return;
  }

  const normalize = (value) => {
    return String(value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim();
  };

  const getActiveSort = () => {
    return priceTabs?.querySelector("button.active")?.dataset.sort || "";
  };

  const getActiveStatus = () => {
    return statusTabs?.querySelector("button.active")?.dataset.status || "";
  };

  const applyAllSpecialistFilters = () => {
    const query = normalize(searchInput?.value || "");
    const activeSort = getActiveSort();
    const activeStatus = getActiveStatus();

    let visibleCards = [];

    cards.forEach((card) => {
      const searchableText = normalize(card.dataset.search || card.textContent);
      const isOnline = card.dataset.online === "true";

      const matchesSearch = !query || searchableText.includes(query);
      const matchesStatus =
        !activeStatus ||
        (activeStatus === "online" && isOnline) ||
        (activeStatus === "offline" && !isOnline);

      const shouldShow = matchesSearch && matchesStatus;

      card.classList.toggle("is-hidden-by-search", !shouldShow);

      if (shouldShow) {
        visibleCards.push(card);
      }
    });

    if (activeSort) {
      visibleCards
        .sort((a, b) => {
          const priceA = Number(a.dataset.price || 0);
          const priceB = Number(b.dataset.price || 0);

          if (activeSort === "menor_preco") {
            return priceA - priceB;
          }

          if (activeSort === "maior_preco") {
            return priceB - priceA;
          }

          return 0;
        })
        .forEach((card) => {
          card.parentElement.appendChild(card);
        });
    }

    if (counter) {
      if (!visibleCards.length) {
        counter.textContent = "Nenhum especialista encontrado";
      } else if (visibleCards.length === 1) {
        counter.textContent = "Mostrando 1 especialista";
      } else {
        counter.textContent = `Mostrando ${visibleCards.length} especialistas`;
      }
    }
  };

  statusTabs.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      statusTabs.querySelectorAll("button").forEach((item) => {
        item.classList.remove("active");
      });

      button.classList.add("active");
      applyAllSpecialistFilters();
    });
  });

  searchInput?.addEventListener("input", () => {
    requestAnimationFrame(applyAllSpecialistFilters);
  });

  priceTabs?.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      requestAnimationFrame(applyAllSpecialistFilters);
    });
  });

  clearButton?.addEventListener("click", () => {
    requestAnimationFrame(() => {
      statusTabs.querySelectorAll("button").forEach((button) => {
        button.classList.toggle("active", button.dataset.status === "");
      });

      applyAllSpecialistFilters();
    });
  });

  applyAllSpecialistFilters();
});


// SEVERINO CHAT JS
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("severinoChatForm");
  const input = document.getElementById("severinoChatInput");
  const chatBox = document.getElementById("severinoChatBox");

  if (!form || !input || !chatBox) {
    return;
  }

  let severinoUserName = "";
  let severinoStep = "apresentacao";

  const cleanName = (value) => {
    return String(value || "")
      .replace(/[^A-Za-zÀ-ÿ\s]/g, "")
      .trim()
      .split(" ")[0];
  };

  const addMessage = ({ author, text, type, actionLabel, actionUrl }) => {
    chatBox.classList.remove("empty");

    const message = document.createElement("div");
    message.className = `severino-message ${type}`;

    const strong = document.createElement("strong");
    strong.textContent = author;

    const span = document.createElement("span");
    span.textContent = text;

    message.appendChild(strong);
    message.appendChild(span);

    if (actionLabel && actionUrl) {
      const link = document.createElement("a");
      link.className = "severino-action-link";
      link.href = actionUrl;
      link.textContent = actionLabel;
      message.appendChild(link);
    }

    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;
  };

  const askSeverino = async (mensagem) => {
    const response = await fetch("/api/severino/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ mensagem })
    });

    return await response.json();
  };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const mensagem = input.value.trim();

    if (!mensagem) {
      return;
    }

    const button = form.querySelector("button");
    button.disabled = true;

    addMessage({
      author: "Você",
      text: mensagem,
      type: "severino-user"
    });

    input.value = "";

    if (severinoStep === "apresentacao") {
      severinoStep = "nome";

      addMessage({
        author: "Severino",
        text: "Olá! Eu sou o Severino, mascote do Tele-Severino. Estou bem feliz em te atender por aqui. Como você está hoje? Antes de continuar, me fala seu primeiro nome?",
        type: "severino-bot"
      });

      button.disabled = false;
      input.focus();
      return;
    }

    if (severinoStep === "nome") {
      const nome = cleanName(mensagem);

      if (!nome || nome.length < 2) {
        addMessage({
          author: "Severino",
          text: "Opa, não consegui pegar seu nome direitinho. Pode me falar só seu primeiro nome?",
          type: "severino-bot"
        });

        button.disabled = false;
        input.focus();
        return;
      }

      severinoUserName = nome;
      severinoStep = "duvida";

      addMessage({
        author: "Severino",
        text: `Prazer, ${nome}! Agora me conta: qual problema você precisa resolver hoje? Pode ser algo como chuveiro, computador, receita, estudos ou atendimento online.`,
        type: "severino-bot"
      });

      button.disabled = false;
      input.focus();
      return;
    }

    addMessage({
      author: "Severino",
      text: `${severinoUserName ? severinoUserName + ", " : ""}só um instante, estou procurando a melhor orientação para você...`,
      type: "severino-bot"
    });

    const loadingMessage = chatBox.lastElementChild;

    try {
      const data = await askSeverino(mensagem);

      if (loadingMessage) {
        loadingMessage.remove();
      }

      const respostaFinal = severinoUserName
        ? `${severinoUserName}, ${data.resposta || "não consegui entender, mas posso te mostrar os especialistas disponíveis."}`
        : data.resposta || "Não consegui entender, mas posso te mostrar os especialistas disponíveis.";

      addMessage({
        author: "Severino",
        text: respostaFinal,
        type: "severino-bot",
        actionLabel: data.acao_label || "Ver especialistas",
        actionUrl: data.acao_url || "/especialistas"
      });

    } catch (error) {
      if (loadingMessage) {
        loadingMessage.remove();
      }

      addMessage({
        author: "Severino",
        text: "Tive um problema para responder agora, mas você pode ver todos os especialistas disponíveis.",
        type: "severino-bot",
        actionLabel: "Ver especialistas",
        actionUrl: "/especialistas"
      });

    } finally {
      button.disabled = false;
      input.focus();
    }
  });
});


// CLIENT MESSAGE SYSTEM SINGLE SOURCE FINAL
(() => {
  const QUICK_REPLY_STORAGE = "teleSeverinoQuickReplyMessages";
  const HIDDEN_STORAGE = "teleSeverinoHiddenPreviewThreads";
  const READ_STORAGE = "teleSeverinoReadPreviewThreads";

  function safeParse(value, fallback) {
    try {
      return JSON.parse(value || "");
    } catch {
      return fallback;
    }
  }

  function getReplies() {
    return safeParse(localStorage.getItem(QUICK_REPLY_STORAGE), {});
  }

  function setReplies(data) {
    try {
      localStorage.setItem(QUICK_REPLY_STORAGE, JSON.stringify(data));
    } catch {}
  }

  function getHiddenThreads() {
    return new Set(safeParse(localStorage.getItem(HIDDEN_STORAGE), []));
  }

  function setHiddenThreads(data) {
    try {
      localStorage.setItem(HIDDEN_STORAGE, JSON.stringify(Array.from(data)));
    } catch {}
  }

  function getReadThreads() {
    return new Set(safeParse(localStorage.getItem(READ_STORAGE), []));
  }

  function setReadThreads(data) {
    try {
      localStorage.setItem(READ_STORAGE, JSON.stringify(Array.from(data)));
    } catch {}
  }

  function getEls() {
    return {
      dock: document.getElementById("clientMessageDock"),
      pill: document.getElementById("clientMessagePill"),
      panel: document.getElementById("clientMessagePanel"),
      list: document.querySelector("[data-floating-message-list]")
    };
  }

  function removeQuickReply() {
    document.querySelectorAll(".client-quick-reply").forEach((item) => item.remove());
    document.querySelectorAll(".client-message-row.is-selected").forEach((row) => {
      row.classList.remove("is-selected");
    });
  }

  function getVisibleUnreadRows() {
    return Array.from(document.querySelectorAll("[data-floating-message-preview]")).filter((row) => {
      return row.style.display !== "none" && !row.classList.contains("is-quick-replied");
    });
  }

  function applyHiddenRows() {
    const hidden = getHiddenThreads();

    document.querySelectorAll("[data-floating-message-preview]").forEach((row) => {
      const id = row.getAttribute("data-floating-message-preview");
      const shouldHide = hidden.has(id);

      row.classList.toggle("is-quick-replied", shouldHide);
      row.style.display = shouldHide ? "none" : "";
    });

    refreshEmptyState();
  }

  function applyReadState() {
    const read = getReadThreads();

    document.querySelectorAll("[data-preview-thread]").forEach((avatar) => {
      const id = avatar.getAttribute("data-preview-thread");
      avatar.classList.toggle("is-read", read.has(id));
    });
  }

  function refreshEmptyState() {
    const { dock, list } = getEls();

    if (!dock || !list) {
      return;
    }

    const visible = getVisibleUnreadRows();
    let empty = list.querySelector(".client-message-empty-state");

    if (visible.length > 0) {
      dock.classList.remove("no-unread");

      if (empty) {
        empty.remove();
      }

      return;
    }

    dock.classList.add("no-unread");

    if (!empty) {
      empty = document.createElement("div");
      empty.className = "client-message-empty-state";
      empty.innerHTML = `
        <strong>Nenhuma mensagem nova</strong>
        <span>Use os atalhos abaixo para abrir conversas recentes.</span>
      `;
      list.appendChild(empty);
    }
  }

  function openPanel() {
    const { dock, pill, list } = getEls();

    if (!dock || !pill || !list) {
      return;
    }

    removeQuickReply();
    applyHiddenRows();

    dock.classList.add("open");
    pill.setAttribute("aria-expanded", "true");
    list.classList.remove("is-hidden");

    refreshEmptyState();
  }

  function closePanel() {
    const { dock, pill, list } = getEls();

    if (!dock || !pill || !list) {
      return;
    }

    removeQuickReply();

    dock.classList.remove("open");
    pill.setAttribute("aria-expanded", "false");
    list.classList.remove("is-hidden");
  }

  function markRead(id) {
    const normalizedId = String(id || "").replace("dock-thread-", "");
    const read = getReadThreads();

    read.add(normalizedId);
    setReadThreads(read);

    document.querySelectorAll("[data-preview-thread]").forEach((avatar) => {
      const avatarId = String(avatar.getAttribute("data-preview-thread") || "").replace("dock-thread-", "");
      avatar.classList.toggle("is-read", avatarId === normalizedId);
    });

    const { dock } = getEls();

    if (dock && getVisibleUnreadRows().length > 0) {
      dock.classList.remove("no-unread");
      dock.classList.remove("notifications-read");
    }
  }

  function hideUnreadRow(id) {
    const hidden = getHiddenThreads();

    hidden.add(id);
    setHiddenThreads(hidden);

    document.querySelectorAll(`[data-floating-message-preview="${id}"]`).forEach((row) => {
      row.classList.add("is-quick-replied");
      row.style.display = "none";
    });

    refreshEmptyState();
  }

  function saveReply(id, text) {
    const data = getReplies();

    if (!data[id]) {
      data[id] = [];
    }

    data[id].push({
      text,
      createdAt: new Date().toISOString()
    });

    setReplies(data);
  }

  function syncPreviewRows() {
    const data = getReplies();

    Object.entries(data).forEach(([id, messages]) => {
      if (!Array.isArray(messages) || messages.length === 0) {
        return;
      }

      const last = messages[messages.length - 1];

      document.querySelectorAll(`[data-open-page-thread="page-thread-${id}"] .client-message-history-content span`).forEach((item) => {
        item.textContent = `Você: ${last.text}`;
      });
    });
  }

  function syncPageThreads() {
    const data = getReplies();

    Object.entries(data).forEach(([id, messages]) => {
      const bubbles = document.querySelector(`#page-thread-${id} .client-thread-bubbles`);

      if (!bubbles || !Array.isArray(messages)) {
        return;
      }

      bubbles.querySelectorAll("[data-local-quick-reply]").forEach((item) => item.remove());

      messages.forEach((message) => {
        const bubble = document.createElement("span");
        bubble.className = "me";
        bubble.dataset.localQuickReply = "true";
        bubble.textContent = message.text;
        bubbles.appendChild(bubble);
      });
    });
  }

  function openFullConversation(id) {
    window.location.href = `/cliente/mensagens?conversa=${encodeURIComponent(id)}`;
  }

  function openQuickReply(id) {
    const row = document.querySelector(`[data-floating-message-preview="${id}"]`);

    if (!row) {
      return;
    }

    openPanel();
    removeQuickReply();

    row.classList.add("is-selected");
    markRead(id);

    const reply = document.createElement("div");
    reply.className = "client-quick-reply";
    reply.dataset.replyTo = id;
    reply.innerHTML = `
      <form class="client-quick-reply-form">
        <input type="text" placeholder="Responder rápido..." autocomplete="off">
        <button type="submit" aria-label="Enviar resposta rápida">Enviar</button>
      </form>
      <div class="client-quick-reply-feedback" role="status">
        Mensagem enviada.
      </div>
    `;

    row.insertAdjacentElement("afterend", reply);

    setTimeout(() => {
      reply.querySelector("input")?.focus();
    }, 100);
  }

  function preparePageThreadComposer(thread) {
    if (!thread || thread.querySelector(".client-page-reply-form")) {
      return;
    }

    const id = thread.id.replace("page-thread-", "");

    const form = document.createElement("form");
    form.className = "client-page-reply-form";
    form.innerHTML = `
      <input type="text" placeholder="Digite uma mensagem..." autocomplete="off">
      <button type="submit" aria-label="Enviar mensagem">Enviar</button>
    `;

    form.addEventListener("submit", (event) => {
      event.preventDefault();

      const input = form.querySelector("input");
      const value = input?.value?.trim();

      if (!value) {
        input?.focus();
        return;
      }

      saveReply(id, value);
      syncPreviewRows();
      syncPageThreads();

      input.value = "";
      input.focus();
    });

    thread.appendChild(form);
  }

  function openPageThread(threadId, row) {
    const thread = document.getElementById(threadId);

    if (!thread || !row) {
      return;
    }

    document.querySelectorAll("[data-page-thread]").forEach((item) => {
      item.classList.add("is-hidden");
      item.classList.remove("inline-thread");
    });

    thread.classList.remove("is-hidden");
    thread.classList.add("inline-thread");

    row.insertAdjacentElement("afterend", thread);
    preparePageThreadComposer(thread);
    syncPageThreads();

    thread.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function openThreadFromQuery() {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("conversa");

    if (!id) {
      return;
    }

    const row = document.querySelector(`[data-open-page-thread="page-thread-${id}"]`);

    if (row) {
      setTimeout(() => row.click(), 100);
    }
  }

  document.addEventListener("click", (event) => {
    const target = event.target;

    if (!(target instanceof Element)) {
      return;
    }

    const { dock } = getEls();

    const closeButton = target.closest("#clientCloseMessages");
    const pill = target.closest("#clientMessagePill");
    const avatar = target.closest("[data-preview-thread]");
    const row = target.closest("[data-floating-message-preview]");
    const quickReply = target.closest(".client-quick-reply");
    const pageRow = target.closest("[data-open-page-thread]");
    const pageBack = target.closest("[data-page-thread-back]");

    if (closeButton) {
      event.preventDefault();
      event.stopPropagation();
      closePanel();
      return;
    }

    if (avatar) {
      event.preventDefault();
      event.stopPropagation();

      const id = avatar.getAttribute("data-preview-thread");

      if (!id) {
        return;
      }

      if (dock?.classList.contains("no-unread")) {
        openFullConversation(id);
      } else {
        openQuickReply(id);
      }

      return;
    }

    if (row) {
      event.preventDefault();
      event.stopPropagation();

      const id = row.getAttribute("data-floating-message-preview");

      if (id) {
        openQuickReply(id);
      }

      return;
    }

    if (pill) {
      event.preventDefault();
      event.stopPropagation();

      if (dock?.classList.contains("open")) {
        closePanel();
      } else {
        openPanel();
      }

      return;
    }

    if (quickReply) {
      event.stopPropagation();
      return;
    }

    if (pageRow) {
      event.preventDefault();

      const threadId = pageRow.getAttribute("data-open-page-thread");
      openPageThread(threadId, pageRow);
      return;
    }

    if (pageBack) {
      event.preventDefault();

      document.querySelectorAll("[data-page-thread]").forEach((thread) => {
        thread.classList.add("is-hidden");
        thread.classList.remove("inline-thread");
      });

      return;
    }

    if (dock?.classList.contains("open") && !target.closest("#clientMessageDock")) {
      closePanel();
    }
  }, true);

  document.addEventListener("submit", (event) => {
    const target = event.target;

    if (!(target instanceof Element)) {
      return;
    }

    const form = target.closest(".client-quick-reply-form");

    if (!form) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();

    const reply = form.closest(".client-quick-reply");
    const id = reply?.dataset.replyTo;
    const input = form.querySelector("input");
    const value = input?.value?.trim();

    if (!reply || !id || !value) {
      input?.focus();
      return;
    }

    saveReply(id, value);
    syncPreviewRows();
    syncPageThreads();

    input.value = "";
    input.blur();

    reply.classList.add("sent");

    setTimeout(() => {
      hideUnreadRow(id);
      reply.remove();

      document.querySelectorAll(".client-message-row.is-selected").forEach((item) => {
        item.classList.remove("is-selected");
      });
    }, 1200);
  }, true);

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closePanel();
    }
  });

  function init() {
    applyReadState();
    applyHiddenRows();
    syncPreviewRows();
    syncPageThreads();

    document.querySelectorAll("[data-page-thread]").forEach((thread) => {
      preparePageThreadComposer(thread);
    });

    openThreadFromQuery();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.addEventListener("pageshow", init);
})();
// END CLIENT MESSAGE SYSTEM SINGLE SOURCE FINAL



// PROFILE_COST_ESTIMATOR
(() => {
  const estimator = document.querySelector(".cost-estimator-card");

  if (!estimator) return;

  const buttons = estimator.querySelectorAll("[data-minutes]");
  const estimateMinutes = document.getElementById("estimateMinutes");
  const estimateValue = document.getElementById("estimateValue");

  function parsePrice(value) {
    return Number(
      String(value || "0")
        .replace("R$", "")
        .replace(/\./g, "")
        .replace(",", ".")
        .trim()
    ) || 0;
  }

  function formatMoney(value) {
    return value.toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL"
    });
  }

  function updateEstimate(minutes) {
    const pricePerMinute = parsePrice(estimator.dataset.minutePrice);
    const total = pricePerMinute * Number(minutes || 0);

    if (estimateMinutes) {
      estimateMinutes.textContent = `${minutes} min`;
    }

    if (estimateValue) {
      estimateValue.textContent = formatMoney(total);
    }
  }

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      buttons.forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      updateEstimate(button.dataset.minutes);
    });
  });

  updateEstimate(15);
})();


// CLIENT MORE MENU AND THEME
(() => {
  function initClientMoreMenu() {
    const moreToggle = document.getElementById("clientMoreToggle");
    const moreMenu = document.getElementById("clientMoreMenu");
    const themeButtons = Array.from(document.querySelectorAll("[data-client-theme]"));

    const savedTheme = localStorage.getItem("teleSeverinoTheme") || "light";

    function applyTheme(theme) {
      const normalizedTheme = theme === "dark" ? "dark" : "light";
      const isDark = normalizedTheme === "dark";

      document.body.classList.toggle("client-theme-dark", isDark);
      localStorage.setItem("teleSeverinoTheme", normalizedTheme);

      themeButtons.forEach((button) => {
        const isActive = button.dataset.clientTheme === normalizedTheme;
        button.classList.toggle("is-active", isActive);
        button.setAttribute("aria-pressed", String(isActive));
      });
    }

    applyTheme(savedTheme);

    if (!moreToggle || !moreMenu) {
      return;
    }

    function closeMenu() {
      moreMenu.classList.remove("is-open");
      moreToggle.classList.remove("is-open");
      moreToggle.setAttribute("aria-expanded", "false");
      moreMenu.setAttribute("aria-hidden", "true");
    }

    function openMenu() {
      moreMenu.classList.add("is-open");
      moreToggle.classList.add("is-open");
      moreToggle.setAttribute("aria-expanded", "true");
      moreMenu.setAttribute("aria-hidden", "false");
    }

    moreToggle.addEventListener("click", (event) => {
      event.stopPropagation();

      if (moreMenu.classList.contains("is-open")) {
        closeMenu();
      } else {
        openMenu();
      }
    });

    moreMenu.addEventListener("click", (event) => {
      event.stopPropagation();
    });

    themeButtons.forEach((button) => {
      button.addEventListener("click", () => {
        applyTheme(button.dataset.clientTheme);
      });
    });

    document.addEventListener("click", closeMenu);

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeMenu();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initClientMoreMenu);
  } else {
    initClientMoreMenu();
  }
})();
// END CLIENT MORE MENU AND THEME

/* CLIENT CLOSE MODALS ON OUTSIDE CLICK FINAL */
document.addEventListener("click", function (event) {
  const target = event.target;

  if (!(target instanceof Element)) {
    return;
  }

  const clickInside = function (selector) {
    const element = document.querySelector(selector);
    return element && element.contains(target);
  };

  const closeByButton = function (container) {
    const closeButton = container.querySelector(
      '[data-close-modal], .modal-close, .payment-modal-close, .client-modal-close, .photo-modal-close, .schedule-modal-close, #clientCloseMessages, #closePaymentModal, #closePhotoModal'
    );

    if (closeButton) {
      closeButton.click();
      return true;
    }

    return false;
  };

  document.querySelectorAll(
    '.payment-modal-backdrop:not(.is-hidden), .modal-backdrop:not(.is-hidden), .client-modal-backdrop:not(.is-hidden), .photo-modal-backdrop:not(.is-hidden), .schedule-modal-backdrop:not(.is-hidden)'
  ).forEach(function (backdrop) {
    if (target === backdrop) {
      if (!closeByButton(backdrop)) {
        backdrop.classList.add("is-hidden");
        backdrop.setAttribute("aria-hidden", "true");
        document.body.classList.remove("modal-open");
      }
    }
  });

  const messageDock = document.getElementById("clientMessageDock");
  if (messageDock && messageDock.classList.contains("open") && !messageDock.contains(target)) {
    messageDock.classList.remove("open");
  }

  const moreMenu = document.getElementById("clientMoreMenu");
  const moreToggle = document.getElementById("clientMoreToggle");

  if (
    moreMenu &&
    moreToggle &&
    moreMenu.getAttribute("aria-hidden") === "false" &&
    !moreMenu.contains(target) &&
    !moreToggle.contains(target)
  ) {
    moreMenu.setAttribute("aria-hidden", "true");
    moreToggle.setAttribute("aria-expanded", "false");
  }
});



