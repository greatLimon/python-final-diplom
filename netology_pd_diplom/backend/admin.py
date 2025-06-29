from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from backend.models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact, ConfirmEmailToken

from import_export.admin import ImportExportModelAdmin

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Панель управления пользователями
    """
    model = User

    fieldsets = (
        (None, {'fields': ('email', 'password', 'type')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'company', 'position')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'state', 'import_button')
    actions = ['import_products']

    def import_button(self, obj):
        return format_html(
            '<a class="button" href="/api/v1/partner/import/?url=ВАШ_URL_ИМПОРТА&shop_id={}">Импорт</a>',
            obj.id
        )
    import_button.short_description = 'Импорт товаров'
    import_button.allow_tags = True

    def import_products(self, request, queryset):
        for shop in queryset:
            if shop.url:
                do_import.delay(shop.id, shop.url)
        self.message_user(request, "Задачи на импорт поставлены в очередь")
    import_products.short_description = "Запустить импорт для выбранных магазинов"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')

class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 1

@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    inlines = [ProductParameterInline]
    list_display = ('product', 'shop', 'quantity', 'price', 'price_rrc')
    list_filter = ('shop', 'product__category')
    search_fields = ('product__name', 'model', 'external_id')
    list_editable = ('quantity', 'price', 'price_rrc')
    ordering = ('shop', 'product')


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('product_info', 'parameter', 'value')
    list_filter = ('parameter',)
    search_fields = ('product_info__product__name', 'parameter__name')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    actions = ['mark_as_sent']
    list_display = ('id', 'user', 'dt', 'state', 'contact')
    list_filter = ('state', 'dt')
    search_fields = ('user__email', 'contact__phone')
    date_hierarchy = 'dt'
    readonly_fields = ('dt',)

    @admin.action(description="Пометить как отправленные")
    def mark_as_sent(self, request, queryset):
        queryset.update(state='sent')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_info', 'quantity')
    list_filter = ('order__state',)
    search_fields = ('order__id', 'product_info__product__name')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'street', 'house', 'phone')
    search_fields = ('user__email', 'city', 'street', 'phone')


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at',)
    search_fields = ('user__email', 'key')
