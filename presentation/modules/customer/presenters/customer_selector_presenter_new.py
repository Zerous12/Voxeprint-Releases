"""
Presenter mejorado para la selección de clientes
Contiene toda la lógica de negocio siguiendo el patrón MVP con Facade
"""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog
from typing import List, Dict, Any, Optional
from domain.models.customer import Customer
from application.facades.voxeprint_facade import VoxeprintFacade
from presentation.modules.customer.views.customer_selector_dialog_new import CustomerSelectorDialogNew
from core.utils.logger import logger

class CustomerSelectorPresenterNew:
    """
    Presenter para la ventana de selección de clientes
    Contiene toda la lógica de negocio, la vista solo maneja UI
    Sigue patrón MVP con inyección de dependencias (Facade)
    """

    def __init__(self, parent=None):  
        self.parent = parent     
        self.view = None        
        
        # Facade para operaciones de negocio (inyección de dependencias)
        self.facade: Optional[VoxeprintFacade] = None
        
        # Estado interno
        self.all_customers: List[Customer] = []
        self.filtered_customers: List[Customer] = []
        self.selected_customer: Optional[Customer] = None
        
        # Timer para búsqueda con delay
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
    
    def set_facade(self, facade: VoxeprintFacade):
        """Establece el facade para acceso a datos"""
        self.facade = facade
        
        
    
    def run(self):
        # Crear vista con un QWidget válido como parent
        self.view = CustomerSelectorDialogNew(self.parent)
        # Variable para el último texto de búsqueda
        self.current_search_text = ""
        # Conectar señales de la vista
        self._connect_view_signals()
        # Cargar datos inicial
        self._load_initial_data()
        # Ejecutar diálogo y devolver el cliente seleccionado
        result = self.view.exec()
        if result == QDialog.Accepted:
            return self.get_selected_customer()
        return None


    def _connect_view_signals(self):
        """Conecta las señales de la vista al presenter"""
        self.view.search_requested.connect(self._on_search_requested)
        self.view.refresh_requested.connect(self._on_refresh_requested)
        self.view.customer_selected.connect(self._on_customer_selected)
        self.view.add_customer_requested.connect(self._on_add_customer_requested)
    
    def _load_initial_data(self):
        """Carga los datos iniciales"""
        self.view.show_loading("Cargando clientes disponibles...")
        
        # Usar timer para no bloquear la UI
        QTimer.singleShot(100, self._load_customers_from_db)
    
    def _load_customers_from_db(self):
        """Carga clientes desde la base de datos usando facade"""
        try:
            if self.facade:
                # Usar facade para obtener todos los clientes
                response = self.facade.search_customers()
                if response.success:
                    self.all_customers = response.data or []
                    
                    # Ordenar por ID de menor a mayor (consistencia con inventario)
                    self.all_customers.sort(key=lambda customer: customer.id if customer.id is not None else 0)
                    self.filtered_customers = self.all_customers.copy()
                    
                    if self.all_customers:
                        logger.info("CustomerSelector", "Clientes cargados para selector", 
                                       cantidad=len(self.all_customers))
                        self._update_view_with_customers(self.all_customers)
                    else:
                        logger.warning("CustomerSelector", "No se encontraron clientes en la base de datos")
                        self.view.show_no_results("No hay clientes registrados en la base de datos")
                else:
                    logger.error("CustomerSelector", f"Error desde facade: {response.message}")
                    self.view.show_no_results(f"Error: {response.message}")
            else:
                logger.error("CustomerSelector", "No hay conexión al facade")
                self.view.show_no_results("Error: No hay conexión al facade")
                
        except Exception as e:
            logger.error("CustomerSelector", f"Error cargando clientes: {e}")
            self.view.show_no_results(f"Error cargando clientes: {str(e)}")
        
        finally:
            self.view.hide_loading()
        
    def _update_view_with_customers(self, customers: List[Customer]):
        """Actualiza la vista con la lista de clientes"""
        # Convertir a diccionarios para la vista
        customers_data = []
        for customer in customers:
            customers_data.append({
                'id': customer.id,
                'full_name': customer.full_name or '',  # Asegurar que no sea None
                'ruc_ci': customer.ruc_ci or '',
                'email': customer.email or '',
                'phone_number': customer.phone_number or '',
                'is_default': customer.is_default,
                'created_at': customer.created_at or '',
                'updated_at': customer.updated_at or ''
            })
        
        self.view.populate_table(customers_data)
    
    def _on_search_requested(self, search_text: str):
        """Maneja la solicitud de búsqueda"""
        # Usar timer para evitar búsquedas excesivas
        self.search_timer.stop()
        self.current_search_text = search_text
        self.search_timer.start(300)  # 300ms de delay
    
    def _perform_search(self):
        """Realiza la búsqueda con el texto actual"""
        search_text = self.current_search_text.lower().strip()
        
        if not search_text:
            # Si no hay texto, mostrar todos (ya ordenados por ID)
            self.filtered_customers = self.all_customers.copy()
        else:
            # Filtrar clientes
            self.filtered_customers = []
            
            for customer in self.all_customers:
                # Buscar en múltiples campos
                search_fields = [
                    customer.full_name.lower(),
                    (customer.ruc_ci or "").lower(),
                    (customer.email or "").lower(),
                    (customer.phone_number or "").lower()
                ]
                
                # Si algún campo contiene el texto de búsqueda
                if any(search_text in field for field in search_fields):
                    self.filtered_customers.append(customer)
            
            # Mantener orden por ID en los resultados filtrados
            self.filtered_customers.sort(key=lambda customer: customer.id if customer.id is not None else 0)
        
        # Actualizar vista
        if self.filtered_customers:
            self._update_view_with_customers(self.filtered_customers)
            logger.debug("CustomerSelector", f"Búsqueda '{search_text}': {len(self.filtered_customers)} resultados")
        else:
            if search_text:
                self.view.show_no_results(f"No se encontraron clientes que contengan '{search_text}'")
            else:
                self.view.show_no_results("No hay clientes disponibles")
    
    def _on_refresh_requested(self):
        """Maneja la solicitud de actualización"""
        self.view.show_loading("Actualizando lista de clientes...")
        
        # Limpiar filtros
        self.view.clear_search_text()
        self.current_search_text = ""
        
        # Recargar desde base de datos
        QTimer.singleShot(500, self._load_customers_from_db)
    
    def _on_customer_selected(self, customer_data: Dict[str, Any]):
        """Maneja la selección de un cliente"""
        # Buscar el cliente completo por ID
        customer_id = customer_data.get('id')
        selected_customer = None
        
        for customer in self.all_customers:
            if customer.id == customer_id:
                selected_customer = customer
                break
        
        if selected_customer:
            self.selected_customer = selected_customer
        else:
            logger.error("CustomerSelector", f"No se encontró el cliente con ID {customer_id}")
    
    def _on_add_customer_requested(self):
        """Maneja la solicitud de agregar nuevo cliente"""
        # Abrir el diálogo de agregar cliente
        from presentation.modules.customer.views.add_customer_dialog import AddCustomerDialog
        dialog = AddCustomerDialog(self.view)
        new_customer_data = None
        def on_customer_added(data):
            nonlocal new_customer_data
            new_customer_data = data
        dialog.customer_added.connect(on_customer_added)
        if dialog.exec() == QDialog.DialogCode.Accepted and new_customer_data:
            # Recargar la lista de clientes desde la base de datos
            self._load_customers_from_db()
            # Buscar el nuevo cliente en la lista y seleccionarlo
            customer_id = new_customer_data.get('id')
            for idx, customer in enumerate(self.all_customers):
                if customer.id == customer_id:
                    # Actualizar la tabla y seleccionar el nuevo cliente
                    self.filtered_customers = [customer]
                    self._update_view_with_customers(self.filtered_customers)
                    # Actualizar selección en la vista
                    self.view.set_selected_customer_info({
                        'id': customer.id,
                        'full_name': customer.full_name,
                        'ruc_ci': customer.ruc_ci,
                        'email': customer.email,
                        'phone_number': customer.phone_number,
                        'is_default': customer.is_default,
                        'created_at': customer.created_at,
                        'updated_at': customer.updated_at
                    })
                    break
    
    def get_selected_customer(self) -> Optional[Customer]:
        """Retorna el cliente seleccionado"""
        return self.selected_customer
    
    def search_customers(self, search_text: str) -> List[Customer]:
        """Busca clientes que coincidan con el texto"""
        if not search_text:
            return self.all_customers.copy()
        
        search_text = search_text.lower()
        results = []
        
        for customer in self.all_customers:
            # Campos de búsqueda
            searchable_text = f"{customer.full_name} {customer.ruc_ci} {customer.email} {customer.phone_number}".lower()
            
            if search_text in searchable_text:
                results.append(customer)
        
        return results
    
    def get_default_customer(self) -> Optional[Customer]:
        """Obtiene el cliente predeterminado"""
        for customer in self.all_customers:
            if customer.is_default:
                return customer
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de los clientes"""
        if not self.all_customers:
            return {}
        
        total_count = len(self.all_customers)
        default_count = sum(1 for c in self.all_customers if c.is_default)
        with_email_count = sum(1 for c in self.all_customers if c.email)
        with_phone_count = sum(1 for c in self.all_customers if c.phone_number)
        with_ruc_ci_count = sum(1 for c in self.all_customers if c.ruc_ci)
        
        return {
            'total_customers': total_count,
            'default_customers': default_count,
            'with_email': with_email_count,
            'with_phone': with_phone_count,
            'with_ruc_ci': with_ruc_ci_count,
            'email_percentage': (with_email_count / total_count * 100) if total_count > 0 else 0,
            'phone_percentage': (with_phone_count / total_count * 100) if total_count > 0 else 0
        }
    
    def validate_customer_selection(self, customer: Customer) -> tuple[bool, str]:
        """Valida si un cliente puede ser seleccionado"""
        if not customer:
            return False, "No hay cliente seleccionado"
        
        # Verificar datos mínimos
        if not customer.full_name:
            return False, "El cliente seleccionado no tiene nombre completo"
        
        return True, "Cliente válido para selección"
    
    def format_customer_summary(self, customer: Customer) -> str:
        """Retorna un resumen formateado del cliente"""
        if not customer:
            return "Ningún cliente seleccionado"
        
        parts = [customer.full_name]
        
        if customer.ruc_ci:
            parts.append(f"({customer.ruc_ci})")
        
        if customer.email:
            parts.append(f"- {customer.email}")
        
        if customer.phone_number:
            parts.append(f"- {customer.phone_number}")
        
        if customer.is_default:
            parts.append("(PREDETERMINADO)")

        return " ".join(parts)
