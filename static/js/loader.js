// Добавьте в конце вашего generate_html() перед закрывающим </body>
<script>
    setTimeout(() => {{
        document.querySelector('.loader-example').style.display = 'none';
        document.querySelector('.news-section').style.display = 'flex';
        document.querySelector('.footer').style.display = 'flex';
    }}, 3000);
</script>