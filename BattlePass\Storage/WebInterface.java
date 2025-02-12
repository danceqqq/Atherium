package me.yourname.testplugin;

import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.BookMeta;
import org.bukkit.inventory.ItemStack;

public class WebInterface {
    private final Main plugin;

    public WebInterface(Main plugin) {
        this.plugin = plugin;
    }

    public void show(Player player) {
        ItemStack book = new ItemStack(Material.WRITTEN_BOOK);
        BookMeta meta = (BookMeta) book.getItemMeta();

        // Заголовок книги
        meta.setTitle("Battle Pass & Хранилище");

        // Страницы
        meta.setPage(1, "Добро пожаловать в Battle Pass!");
        meta.setPage(2, "Здесь вы можете получить награды.");
        meta.setPage(3, "Хранилище доступно по команде /storage.");

        book.setItemMeta(meta);
        player.openBook(book);
    }
}
