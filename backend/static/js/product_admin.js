document.addEventListener("DOMContentLoaded", function () {

    const category = document.getElementById("id_category");

    const price = document.querySelector(".field-price");
    const cookieQuantity = document.querySelector(".field-cookie_quantity");
    const cookiePackPrice = document.querySelector(".field-cookie_pack_price");
    const whippingPrice = document.querySelector(".field-whipping_price");
    const buttercreamPrice = document.querySelector(".field-buttercream_price");

    function hideAllOldFields() {

        if (price) {
            price.style.display = "none";
        }

        if (cookieQuantity) {
            cookieQuantity.style.display = "none";
        }

        if (cookiePackPrice) {
            cookiePackPrice.style.display = "none";
        }

        if (whippingPrice) {
            whippingPrice.style.display = "none";
        }

        if (buttercreamPrice) {
            buttercreamPrice.style.display = "none";
        }
    }

    function updateFields() {

        hideAllOldFields();

        if (!category) {
            return;
        }

        const selectedCategory = category.value;

        // =========================
        // CAKE
        // =========================

        if (selectedCategory === "cake") {

            if (whippingPrice) {
                whippingPrice.style.display = "";
            }

            if (buttercreamPrice) {
                buttercreamPrice.style.display = "";
            }
        }

        // =========================
        // COOKIE
        // =========================

        else if (selectedCategory === "cookie") {

            if (cookieQuantity) {
                cookieQuantity.style.display = "";
            }

            if (cookiePackPrice) {
                cookiePackPrice.style.display = "";
            }
        }

        // =========================
        // OTHER PRODUCTS
        // =========================

        else {

            /*
             * Other products use Product Options.
             *
             * Example:
             *
             * Option Name     Price
             * 6 Pieces        300
             * 9 Pieces        420
             * 12 Pieces       540
             *
             * These are entered manually in Admin.
             */
        }
    }

    // Run when page loads
    updateFields();

    // Run when category changes
    if (category) {
        category.addEventListener("change", updateFields);
    }

});