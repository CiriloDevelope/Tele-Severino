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



// Perfil público: modal fake de disponibilidade.
const openScheduleModal = document.getElementById("openScheduleModal");
const closeScheduleModal = document.getElementById("closeScheduleModal");
const scheduleModal = document.getElementById("scheduleModal");
const scheduleSuccess = document.getElementById("scheduleSuccess");

openScheduleModal?.addEventListener("click", () => {
  scheduleModal?.classList.remove("is-hidden");
});

closeScheduleModal?.addEventListener("click", () => {
  scheduleModal?.classList.add("is-hidden");
});

document.querySelectorAll(".schedule-grid button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".schedule-grid button").forEach((item) => {
      item.classList.remove("active");
    });

    button.classList.add("active");
    scheduleSuccess?.classList.remove("is-hidden");
  });
});



// CALENDARIO_MENSAL_DISPONIBILIDADE
(() => {
  const openScheduleModal = document.getElementById("openScheduleModal");
  const closeScheduleModal = document.getElementById("closeScheduleModal");
  const scheduleModal = document.getElementById("scheduleModal");
  const scheduleSuccess = document.getElementById("scheduleSuccess");
  const scheduleSlotPanel = document.getElementById("scheduleSlotPanel");

  const cupons = {
    "PRIMEIRA10": "Cupom aplicado: 10% de desconto na primeira reserva.",
    "POS20": "Cupom aplicado: melhor condição para horário pós-comercial.",
    "PLUS15": "Cupom aplicado: benefício de agenda Plus.",
    "TESTE5": "Cupom aplicado: desconto de teste do protótipo."
  };

  function resetarPainel() {
    document.querySelectorAll(".schedule-day").forEach((item) => {
      item.classList.remove("active");
    });

    if (scheduleSlotPanel) {
      scheduleSlotPanel.innerHTML = `
        <strong>Selecione um dia disponível</strong>
        <p>Os horários liberados aparecerão aqui.</p>
      `;
    }

    scheduleSuccess?.classList.add("is-hidden");
  }

  function abrirModal() {
    scheduleModal?.classList.remove("is-hidden");
    scheduleSuccess?.classList.add("is-hidden");
  }

  function fecharModal() {
    scheduleModal?.classList.add("is-hidden");
  }

  function montarHorarios(button) {
    const jaSelecionado = button.classList.contains("active");

    if (jaSelecionado) {
      resetarPainel();
      return;
    }

    const day = button.dataset.day;
    const weekday = button.dataset.weekday;
    const slots = (button.dataset.slots || "").split(",").filter(Boolean);

    document.querySelectorAll(".schedule-day").forEach((item) => {
      item.classList.remove("active");
    });

    button.classList.add("active");
    scheduleSuccess?.classList.add("is-hidden");

    if (!scheduleSlotPanel) return;

    scheduleSlotPanel.classList.add("is-changing");

    setTimeout(() => {
      const slotButtons = slots.map((slot, index) => {
        const reservado = (Number(day) + index) % 4 === 0;
        const status = reservado ? "Reservado" : "Livre";
        const classe = reservado ? "reserved" : "free";
        const disabled = reservado ? "disabled" : "";

        return `
          <button type="button" class="schedule-slot ${classe}" ${disabled} data-slot="${slot}">
            <strong>${slot}</strong>
            <small>${status}</small>
          </button>
        `;
      }).join("");

      scheduleSlotPanel.innerHTML = `
        <strong>${weekday}, dia ${day}</strong>
        <p>Escolha um horário livre para reservar sua videochamada.</p>

        <div class="schedule-slots">
          ${slotButtons}
        </div>

        <div class="coupon-area is-hidden" id="couponArea">
          <label for="couponInput">Cupom de desconto</label>
          <div class="coupon-line">
            <input id="couponInput" type="text" placeholder="Ex: PRIMEIRA10 ou POS20">
            <button type="button" id="applyCouponButton">Aplicar</button>
          </div>
          <small id="couponFeedback">
            Dica: cupons podem liberar melhores condições em horários específicos.
          </small>
        </div>
      `;

      scheduleSlotPanel.classList.remove("is-changing");

      scheduleSlotPanel.querySelectorAll(".schedule-slot.free").forEach((slotButton) => {
        slotButton.addEventListener("click", () => {
          scheduleSlotPanel.querySelectorAll(".schedule-slot").forEach((item) => {
            item.classList.remove("active");
          });

          slotButton.classList.add("active");

          const couponArea = document.getElementById("couponArea");
          couponArea?.classList.remove("is-hidden");

          scheduleSuccess?.classList.remove("is-hidden");
          scheduleSuccess.textContent = `Horário ${slotButton.dataset.slot} reservado no protótipo. Você ainda pode aplicar um cupom antes de confirmar.`;
        });
      });

      const applyCouponButton = document.getElementById("applyCouponButton");
      const couponInput = document.getElementById("couponInput");
      const couponFeedback = document.getElementById("couponFeedback");

      applyCouponButton?.addEventListener("click", () => {
        const codigo = String(couponInput?.value || "").trim().toUpperCase();

        if (!codigo) {
          couponFeedback.textContent = "Digite um cupom para validar.";
          couponFeedback.className = "coupon-feedback warning";
          return;
        }

        if (cupons[codigo]) {
          couponFeedback.textContent = cupons[codigo];
          couponFeedback.className = "coupon-feedback success";
          return;
        }

        couponFeedback.textContent = "Cupom não encontrado para este horário.";
        couponFeedback.className = "coupon-feedback error";
      });
    }, 180);
  }

  openScheduleModal?.addEventListener("click", abrirModal);
  closeScheduleModal?.addEventListener("click", fecharModal);

  document.querySelectorAll(".schedule-day:not(.locked)").forEach((button) => {
    button.addEventListener("click", () => montarHorarios(button));
  });
})();



// Solicitação fake do Tele-Severino após seleção de horário.
const confirmScheduleButton = document.getElementById("confirmScheduleButton");

document.addEventListener("click", (event) => {
  const freeSlot = event.target.closest(".schedule-slot.free");

  if (freeSlot && confirmScheduleButton) {
    confirmScheduleButton.disabled = false;
    confirmScheduleButton.classList.add("is-ready");
  }
});

confirmScheduleButton?.addEventListener("click", () => {
  if (confirmScheduleButton.disabled) return;

  const scheduleSuccess = document.getElementById("scheduleSuccess");

  if (scheduleSuccess) {
    scheduleSuccess.classList.remove("is-hidden");
    scheduleSuccess.textContent = "Solicitação Tele-Severino enviada no protótipo. O especialista receberá o pedido de agendamento.";
  }

  confirmScheduleButton.textContent = "Solicitado";
  confirmScheduleButton.disabled = true;
});
