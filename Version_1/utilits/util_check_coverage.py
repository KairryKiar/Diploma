
DOC_ACTIVITIES = {
    "Бизнес-процессы": [
        "SequentialWorkflowActivity",
        "StateMachineWorkflowActivity",
        "StateActivity",
        "TerminateActivity",
        "HandleExternalEventActivity",
        "ListenActivity",
        "DelayActivity",
        "LogActivity",
        "SetStateTitleActivity",
        "SaveHistoryActivity",
        "EmptyBlockActivity",
        "SequenceActivity",
        "ParallelActivity",
        "IfElseActivity",
        "WhileActivity",
    ],
    "Задания": [
        "ApproveActivity",
        "ReviewActivity",
        "RequestInformationActivity",
        "RequestInformationOptionalActivity",
    ],
    "Документ": [
        "SetFieldActivity",
        "SetPermissionsActivity",
        "PublishDocumentActivity",
        "UnPublishDocumentActivity",
        "DeleteDocumentActivity",
        "LockDocumentActivity",
    ],
    "Уведомления": [
        "MailActivity",
        "IMNotifyActivity",
        "ForumReviewActivity",
    ],
    "CRM": [
        "CrmAddProductRow",
        "CrmChangeDealCategoryActivity",
        "CrmChangeStatusActivity",
        "CrmControlNotifyActivity",
        "CrmConvertDocumentActivity",
        "CrmCopyDealActivity",
        "CrmCreateCallActivity",
        "CrmCreateMeetingActivity",
        "CrmCreateTodoActivity",
        "CrmEventAddActivity",
        "CrmGenerateEntityDocumentActivity",
        "CrmGetDataEntityActivity",
        "CrmGetPaymentInfoActivity",
        "CrmGetProductRowActivity",
        "CrmOrderPayActivity",
        "CrmSendEmailActivity",
        "CrmSendSmsActivity",
        "CrmSetCompanyField",
        "CrmSetContactField",
        "CrmSetOrderPaid",
        "CrmTimelineCommentAdd",
        "CrmUpdateDynamicActivity",
        "CrmWaitActivity",
    ],
    "Прочее": [
        "SetVariableActivity",
        "SetConstantActivity",
        "GetUserActivity",
        "GetUserInfoActivity",
        "MathOperationActivity",
        "RandomStringActivity",
    ],
    "Диск": [
        "DiskAddFolderActivity",
        "DiskUploadActivity",
        "DiskRemoveActivity",
    ],
}


our_codes = {
    "ApproveActivity", "DelayActivity", "DiskAddFolderActivity",
    "EmptyBlockActivity", "GetUserActivity", "IMNotifyActivity",
    "IfElseActivity", "IfElseBranchActivity", "LogActivity",
    "RequestInformationActivity", "ReviewActivity", "SequenceActivity",
    "SequentialWorkflowActivity", "SetFieldActivity", "SetPermissionsActivity",
    "SetStateTitleActivity", "SetVariableActivity", "Task2Activity",
    "TerminateActivity", "WhileActivity",
}

total_in_docs = sum(len(v) for v in DOC_ACTIVITIES.values())

print("=" * 60)
print("  СРАВНЕНИЕ: наш каталог vs документация Битрикс")
print("=" * 60)
print()

for group, items in DOC_ACTIVITIES.items():
    print(f"  📁 {group} ({len(items)} шт.)")
    for item in items:
        status = "✅" if item in our_codes else "❌"
        print(f"       {status} {item}")
    print()

print("=" * 60)
print(f"  Всего действий в документации : {total_in_docs}")
print(f"  В нашем activities_catalog    : {len(our_codes)}")
print(f"  Не охвачено                   : {total_in_docs - len(our_codes)}")
print()

coverage_pct = (len(our_codes) / total_in_docs) * 100
print(f"  Покрытие: {len(our_codes)}/{total_in_docs} = {coverage_pct:.1f}%")
print("=" * 60)
