from django.urls import path
from . import views

app_name = 'erp_extension'

urlpatterns = [
    path('' , views.view_clients, name='view_clients'),
    path('trello/', views.TrelloExplorerView.as_view(), name='crm'),
    path('trello/', views.TrelloExplorerView.as_view(), name='trello_explorer'),
    path('trello/workspaces/', views.TrelloExplorerView.as_view(), name='trello_workspaces'),
    path('trello/workspaces/<str:workspace_id>/', views.TrelloExplorerView.as_view(), name='workspace_boards'),
    path('trello/boards/<str:board_id>/', views.TrelloExplorerView.as_view(), name='board_detail'),
    ]

