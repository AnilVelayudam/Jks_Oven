document.addEventListener("DOMContentLoaded", function () {

    function toggleFields() {
        let category = document.getElementById("id_category");

        if (!category) return;

        let value = category.value;

        let priceField = document.querySelector(".form-row.field-price");
        let whippingField = document.querySelector(".form-row.field-whipping_price");
        let butterField = document.querySelector(".form-row.field-buttercream_price");
        let cakeTypeField = document.querySelector(".form-row.field-cake_type");

        if (value === "cake") {
            if (priceField) priceField.style.display = "none";
            if (whippingField) whippingField.style.display = "block";
            if (butterField) butterField.style.display = "block";
            if (cakeTypeField) cakeTypeField.style.display = "block";
        } else {
            if (priceField) priceField.style.display = "block";
            if (whippingField) whippingField.style.display = "none";
            if (butterField) butterField.style.display = "none";
            if (cakeTypeField) cakeTypeField.style.display = "none";
        }
    }

    toggleFields();

    let category = document.getElementById("id_category");
    if (category) {
        category.addEventListener("change", toggleFields);
    }
});