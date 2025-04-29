// tailwind-config.js
tailwind.config = {
    theme: {
        extend: {
            // fontFamily: {
            //     'eb-garamond': ['"EB Garamond"', 'serif'],  // Add EB Garamond font
            // },
            colors: {
                dark_red: "#B23A3B",
                red: "#DA0000",
                popping_red: "#FA0504",
                light_red: "#ffe6e6",
                off_white: "#F5F5F5",
                light_gray :"#d9d9d9",
                gray:"#666666",
                dark_gray:"#333333",
                purple:"#FFD0F2",
                bleu_ciel:"#05C3DD",
                jaune:"#FFD616",
            },
            backgroundImage: {
                'official_gradient': 'linear-gradient(to left, #333333 , #fa0504)',
                'pastel_gradient': 'linear-gradient(to right, #05C3DD, #FFD616)',
                'light_gradient': 'linear-gradient(to right, #F5F5F5, #d9d9d9, #ffe6e6)',
              },
        }
    }
}
// fd9b9b #05C3DD #2596be
//--toastify-color-info: #3498db;
// --toastify-color-success: #07bc0c;
// --toastify-color-warning: #f1c40f;
// --toastify-color-error: #e74c3c;