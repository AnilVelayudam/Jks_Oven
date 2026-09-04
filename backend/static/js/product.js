// ======================================================
// PRODUCT JS
// ======================================================


// ======================================================
// CAKE PRICE
// ======================================================

function getSelectedWeight() {

    let selected = document.querySelector(
        'input[name="weight"]:checked'
    );

    let custom = document.getElementById("customWeight");

    if (custom && custom.value) {
        return parseFloat(custom.value);
    }

    return selected ? parseFloat(selected.value) : 1;
}


function getSelectedCream() {

    let cream = document.querySelector(
        'input[name="cream"]:checked'
    );

    return cream ? cream.value : "whipping";
}


function updatePrice() {

    // Cake pricing
    if (window.basePrices) {

        let cream = getSelectedCream();
        let weight = getSelectedWeight();

        let basePrice = window.basePrices[cream];

        if (
            basePrice === null ||
            basePrice === undefined ||
            isNaN(basePrice)
        ) {
            document.getElementById("price").innerText =
                "Not Available";
            return;
        }

        let finalPrice = basePrice * weight;

        document.getElementById("price").innerText =
            "₹" + finalPrice.toFixed(0);

        return;
    }


    // Product option pricing
    let selectedOption =
        document.querySelector(".product-option-btn.active");

    if (selectedOption) {

        let price = parseFloat(
            selectedOption.dataset.price
        );

        if (!isNaN(price)) {

            document.getElementById("price").innerText =
                "₹" + price.toFixed(0);
        }
    }
}


// ======================================================
// PRODUCT OPTION
// Brownie
// Cheese Cake
// Jar Cake
// Cinnamon Roll
// Donut
// Bomboloni
// Tiramisu
// Cup Cakes
// Muffins
// Tres Leches
// Ice Cream
// ======================================================

function selectProductOption(button) {

    // Remove active from all options
    document.querySelectorAll(
        ".product-option-btn"
    ).forEach(function(btn) {

        btn.classList.remove("active");

    });


    // Add active to selected option
    button.classList.add("active");


    // Get selected price
    let price = parseFloat(
        button.dataset.price
    );


    // Update price
    if (!isNaN(price)) {

        document.getElementById("price").innerText =
            "₹" + price.toFixed(0);
    }
}


// ======================================================
// COOKIE
// ======================================================

function changeCookieQuantity(change) {

    let quantityElement =
        document.getElementById("cookieQuantity");

    let totalQuantityElement =
        document.getElementById("cookieTotalQuantity");


    if (!quantityElement) {
        return;
    }


    let currentQuantity =
        parseInt(quantityElement.innerText) || 1;


    let newQuantity =
        currentQuantity + change;


    // Minimum 1
    if (newQuantity < 1) {
        newQuantity = 1;
    }


    quantityElement.innerText =
        newQuantity;


    // If cookie pack quantity exists
    if (window.cookieQuantity) {

        let cookiesPerPack =
            parseInt(window.cookieQuantity);

        let totalCookies =
            cookiesPerPack * newQuantity;


        if (totalQuantityElement) {

            totalQuantityElement.innerText =
                totalCookies;
        }


        // Price
        if (
            window.cookiePrice !== null &&
            window.cookiePrice !== undefined
        ) {

            let totalPrice =
                parseFloat(window.cookiePrice) *
                newQuantity;


            if (!isNaN(totalPrice)) {

                document.getElementById("price").innerText =
                    "₹" + totalPrice.toFixed(0);
            }
        }
    }
}


// ======================================================
// GET SELECTED PRODUCT OPTION
// ======================================================

function getSelectedProductOption() {

    let selectedOption =
        document.querySelector(
            ".product-option-btn.active"
        );


    if (!selectedOption) {
        return null;
    }


    return {
        id: selectedOption.dataset.optionId,
        name: selectedOption.dataset.optionName,
        price: selectedOption.dataset.price
    };
}


// ======================================================
// ADD TO CART
// ======================================================

let isAdding = false;


function addToCart() {

    if (isAdding) {
        return;
    }


    if (!window.productId) {

        alert("Product error ❌");

        return;
    }


    isAdding = true;


    let btn =
        document.getElementById("addBtn");


    if (btn) {

        btn.disabled = true;

        btn.innerText =
            "Adding...";
    }


    let url =
        `/add-to-cart/${window.productId}/`;



    // ==================================================
    // CAKE
    // ==================================================

    if (window.basePrices) {

        let cream =
            getSelectedCream();

        let weight =
            getSelectedWeight();


        url +=
            `?cream=${encodeURIComponent(cream)}` +
            `&weight=${encodeURIComponent(weight)}`;


        window.location.href =
            url;

        return;
    }



    // ==================================================
    // PRODUCT OPTIONS
    // ==================================================

    let selectedOption =
        getSelectedProductOption();


    if (selectedOption) {

        url +=
            `?option_id=${encodeURIComponent(
                selectedOption.id
            )}`;


        window.location.href =
            url;

        return;
    }



    // ==================================================
    // COOKIE
    // ==================================================

    if (
        window.cookieQuantity !== null &&
        window.cookieQuantity !== undefined
    ) {

        let quantityElement =
            document.getElementById(
                "cookieQuantity"
            );


        let packQuantity =
            quantityElement
                ? parseInt(quantityElement.innerText)
                : 1;


        url +=
            `?cookie_qty=${encodeURIComponent(
                packQuantity
            )}`;


        window.location.href =
            url;

        return;
    }



    // ==================================================
    // NORMAL PRODUCT
    // ==================================================

    window.location.href =
        url;
}


// ======================================================
// ORDER NOW
// ======================================================

let isOrdering = false;


function orderNow() {

    if (isOrdering) {
        return;
    }


    if (!window.productId) {

        alert("Product error ❌");

        return;
    }


    isOrdering = true;


    let buttons =
        document.querySelectorAll(
            ".buy-btn.secondary"
        );


    buttons.forEach(function(btn) {

        btn.disabled = true;

        btn.innerText =
            "Processing...";

    });


    let url =
        `/buy-now/${window.productId}/`;



    // ==================================================
    // CAKE
    // ==================================================

    if (window.basePrices) {

        let cream =
            getSelectedCream();

        let weight =
            getSelectedWeight();


        url +=
            `?cream=${encodeURIComponent(cream)}` +
            `&weight=${encodeURIComponent(weight)}`;


        window.location.href =
            url;

        return;
    }



    // ==================================================
    // PRODUCT OPTIONS
    // ==================================================

    let selectedOption =
        getSelectedProductOption();


    if (selectedOption) {

        url +=
            `?option_id=${encodeURIComponent(
                selectedOption.id
            )}`;


        window.location.href =
            url;

        return;
    }



    // ==================================================
    // COOKIE
    // ==================================================

    if (
        window.cookieQuantity !== null &&
        window.cookieQuantity !== undefined
    ) {

        let quantityElement =
            document.getElementById(
                "cookieQuantity"
            );


        let packQuantity =
            quantityElement
                ? parseInt(quantityElement.innerText)
                : 1;


        url +=
            `?cookie_qty=${encodeURIComponent(
                packQuantity
            )}`;


        window.location.href =
            url;

        return;
    }



    // ==================================================
    // NORMAL PRODUCT
    // ==================================================

    window.location.href =
        url;
}


// ======================================================
// IMAGE SWITCH
// ======================================================

function changeImage(el) {

    const main =
        document.getElementById(
            "mainImage"
        );


    if (!main) {
        return;
    }


    main.src =
        el.src;


    document
        .querySelectorAll(
            ".thumbnail-container img"
        )
        .forEach(function(img) {

            img.classList.remove(
                "active"
            );

        });


    el.classList.add(
        "active"
    );
}


// ======================================================
// PAGE LOAD
// ======================================================

document.addEventListener(
    "DOMContentLoaded",
    function() {


        // ----------------------------------------------
        // Cake
        // ----------------------------------------------

        if (window.basePrices) {

            updatePrice();


            document
                .querySelectorAll(
                    'input[name="cream"]'
                )
                .forEach(function(el) {

                    el.addEventListener(
                        "change",
                        updatePrice
                    );

                });


            document
                .querySelectorAll(
                    'input[name="weight"]'
                )
                .forEach(function(el) {

                    el.addEventListener(
                        "change",
                        function() {

                            let custom =
                                document.getElementById(
                                    "customWeight"
                                );


                            if (custom) {
                                custom.value = "";
                            }


                            updatePrice();

                        }
                    );

                });


            let customInput =
                document.getElementById(
                    "customWeight"
                );


            if (customInput) {

                customInput.addEventListener(
                    "input",
                    function() {

                        document
                            .querySelectorAll(
                                'input[name="weight"]'
                            )
                            .forEach(function(el) {

                                el.checked =
                                    false;

                            });


                        updatePrice();

                    }
                );
            }
        }



        // ----------------------------------------------
        // Product Options
        // ----------------------------------------------

        let firstOption =
            document.querySelector(
                ".product-option-btn"
            );


        if (firstOption) {

            // Make first option active
            document
                .querySelectorAll(
                    ".product-option-btn"
                )
                .forEach(function(btn) {

                    btn.classList.remove(
                        "active"
                    );

                });


            firstOption.classList.add(
                "active"
            );


            // Show first option price
            let firstPrice =
                parseFloat(
                    firstOption.dataset.price
                );


            if (!isNaN(firstPrice)) {

                document.getElementById(
                    "price"
                ).innerText =
                    "₹" +
                    firstPrice.toFixed(0);

            }
        }

    }
);