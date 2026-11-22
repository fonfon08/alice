Unicode true

!include "MUI2.nsh"
!include "LogicLib.nsh"

!ifndef VERSION
  !define VERSION "0.0.0"
!endif
!ifndef PAYLOAD
  !error "PAYLOAD define is required"
!endif
!ifndef OUTFILE
  !define OUTFILE "ALICE-Full-Setup-${VERSION}.exe"
!endif
!ifndef ICON
  !define ICON "icon.ico"
!endif

Name "ALICE ${VERSION}"
OutFile "${OUTFILE}"
InstallDir "$PROGRAMFILES64\ALICE"
InstallDirRegKey HKLM "Software\ALICE" "InstallDir"
RequestExecutionLevel admin
SetCompressor /SOLID lzma
SetCompressorDictSize 64
BrandingText "ALICE ${VERSION} - Windows x64"

VIProductVersion "${VERSION}.0"
VIAddVersionKey /LANG=0 "ProductName" "ALICE"
VIAddVersionKey /LANG=0 "ProductVersion" "${VERSION}"
VIAddVersionKey /LANG=0 "FileVersion" "${VERSION}.0"
VIAddVersionKey /LANG=0 "CompanyName" "fonfon"
VIAddVersionKey /LANG=0 "FileDescription" "ALICE post-exploitation framework"
VIAddVersionKey /LANG=0 "LegalCopyright" "GPLv3"

!define MUI_ABORTWARNING
!define MUI_ICON "${ICON}"
!define MUI_UNICON "${ICON}"

!define MUI_WELCOMEPAGE_TITLE "ALICE ${VERSION}"
!define MUI_WELCOMEPAGE_TEXT "Instalador do framework ALICE para Windows x64.$\r$\n$\r$\nO instalador cria o server Python, instala as dependencias, gera a operator key, instala o console do operador e, opcionalmente, baixa o toolchain de implants (Nim + MinGW) e inicia o server."

!define MUI_FINISHPAGE_RUN "$INSTDIR\client\app\ALICE.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Abrir o console ALICE"
!define MUI_FINISHPAGE_RUN_FUNCTION LaunchClient
!define MUI_FINISHPAGE_TEXT "Server: http://127.0.0.1:9000$\r$\nOperator key: $INSTDIR\server\operator.key$\r$\n$\r$\nConsole: atalho ALICE na area de trabalho$\r$\nServer manual: $INSTDIR\Iniciar Server.bat"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "PortugueseBR"

; ======================================================================================
; SECTIONS
; ======================================================================================

Section "ALICE Server (obrigatorio)" SecServer
  SectionIn RO

  DetailPrint "Verificando Python..."
  nsExec::ExecToStack 'cmd /c python --version'
  Pop $0
  Pop $1
  ${If} $0 != 0
    nsExec::ExecToStack 'cmd /c py -3 --version'
    Pop $0
    Pop $1
    ${If} $0 != 0
      MessageBox MB_ICONSTOP "Python 3 nao encontrado no PATH.$\r$\n$\r$\nInstale em https://www.python.org/downloads/windows/$\r$\nmarque 'Add python.exe to PATH' e rode o instalador de novo."
      Abort
    ${EndIf}
  ${EndIf}

  DetailPrint "Copiando o server..."
  SetOutPath "$INSTDIR"
  File "${PAYLOAD}\alice.py"
  File "${PAYLOAD}\alice.bat"
  File "${PAYLOAD}\README.md"
  File "${PAYLOAD}\LEIA-ME.txt"
  File "${PAYLOAD}\LICENSE"
  File "${PAYLOAD}\DISCLAIMER.md"
  File "${PAYLOAD}\AUTHORS.md"
  File "${PAYLOAD}\Iniciar Server.bat"
  File "${PAYLOAD}\Parar Server.bat"

  SetOutPath "$INSTDIR\server"
  File /r "${PAYLOAD}\server\*.*"
  SetOutPath "$INSTDIR\implants"
  File /r "${PAYLOAD}\implants\*.*"
  SetOutPath "$INSTDIR\install"
  File /r "${PAYLOAD}\install\*.*"

  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\ALICE" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ALICE" "DisplayName" "ALICE"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ALICE" "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ALICE" "Publisher" "fonfon"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ALICE" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ALICE" "DisplayIcon" "$INSTDIR\client\app\ALICE.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ALICE" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ALICE" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ALICE" "NoRepair" 1

  DetailPrint "Criando o virtualenv e instalando dependencias (pode levar alguns minutos)..."
  nsExec::ExecToLog 'cmd /c ""$INSTDIR\install\setup_server.bat""'
  Pop $0
  ${If} $0 != 0
    MessageBox MB_ICONSTOP "Falha na instalacao do server.$\r$\n$\r$\nLog: $INSTDIR\install-server.log"
    Abort
  ${EndIf}
  DetailPrint "Server instalado."
SectionEnd

Section "Console do operador (client)" SecClient
  DetailPrint "Instalando o console..."
  SetOutPath "$INSTDIR\client\app"
  File /r "${PAYLOAD}\client\app\*.*"

  CreateDirectory "$SMPROGRAMS\ALICE"
  CreateShortCut "$SMPROGRAMS\ALICE\ALICE.lnk" "$INSTDIR\client\app\ALICE.exe" "" "$INSTDIR\client\app\ALICE.exe" 0
  CreateShortCut "$DESKTOP\ALICE.lnk" "$INSTDIR\client\app\ALICE.exe" "" "$INSTDIR\client\app\ALICE.exe" 0
  CreateShortCut "$SMPROGRAMS\ALICE\Desinstalar ALICE.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
SectionEnd

Section "Iniciar o server agora" SecStart
  DetailPrint "Iniciando o server e autenticando o console..."
  Delete "$INSTDIR\install-start.ok"
  nsExec::ExecToLog 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$INSTDIR\install\start_server.ps1"'
  Pop $0
  ${IfNot} ${FileExists} "$INSTDIR\install-start.ok"
    MessageBox MB_ICONEXCLAMATION "O server nao subiu automaticamente.$\r$\n$\r$\nRode: $INSTDIR\Iniciar Server.bat$\r$\nLog: $INSTDIR\server\logs\server.out.log"
  ${EndIf}
SectionEnd

Section "Iniciar o server com o Windows" SecAutostart
  CreateShortCut "$SMSTARTUP\ALICE Server.lnk" "wscript.exe" '"$INSTDIR\install\start_server.vbs"' "$INSTDIR\client\app\ALICE.exe" 0
SectionEnd

Section "Toolchain de implants (Nim + MinGW, ~1 GB)" SecToolchain
  DetailPrint "Baixando Nim + MinGW (pode demorar)..."
  nsExec::ExecToLog 'cmd /c ""$INSTDIR\install\setup_toolchain.bat""'
  Pop $0
  ${If} $0 != 0
    MessageBox MB_ICONEXCLAMATION "O toolchain nao foi instalado.$\r$\nO server funciona, mas nao vai compilar implants.$\r$\n$\r$\nLog: $INSTDIR\install-toolchain.log$\r$\nDepois rode: $INSTDIR\install\windows.bat toolchain"
  ${EndIf}
SectionEnd

; ======================================================================================
; DESCRIPTIONS
; ======================================================================================

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecServer} "Server ALICE (Python/FastAPI + SQLite), dependencias, operator key e arquivos base. Obrigatorio."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecClient} "Console do operador (Electron). Cria atalhos na area de trabalho e no menu Iniciar."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecToolchain} "Nim 2.4.2 + MinGW-w64 para compilar implants Windows. Download de aproximadamente 300 MB."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStart} "Inicia o server em background, libera as portas no firewall e grava a configuracao autenticada do console."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecAutostart} "Sobe o server automaticamente no logon do Windows, sem janela."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; ======================================================================================
; FUNCTIONS
; ======================================================================================

Function LaunchClient
  IfFileExists "$INSTDIR\client\app\ALICE.exe" 0 done
  Exec '"$INSTDIR\client\app\ALICE.exe"'
  done:
FunctionEnd

Function .onInit
  ${If} ${FileExists} "$INSTDIR\alice.py"
    MessageBox MB_YESNO|MB_ICONQUESTION "ALICE ja esta instalado em $INSTDIR.$\r$\nContinuar e sobrescrever?" IDYES +2
    Abort
  ${EndIf}
FunctionEnd

; ======================================================================================
; UNINSTALL
; ======================================================================================

Section "Uninstall"
  DetailPrint "Parando processos..."
  nsExec::ExecToLog 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$INSTDIR\install\stop_server.ps1"'
  Pop $0

  Delete "$SMPROGRAMS\ALICE\ALICE.lnk"
  Delete "$SMPROGRAMS\ALICE\Desinstalar ALICE.lnk"
  RMDir "$SMPROGRAMS\ALICE"
  Delete "$DESKTOP\ALICE.lnk"
  Delete "$SMSTARTUP\ALICE Server.lnk"

  ExecWait 'netsh advfirewall firewall delete rule name="ALICE Server"'
  ExecWait 'netsh advfirewall firewall delete rule name="ALICE Listener"'

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ALICE"
  DeleteRegKey HKLM "Software\ALICE"

  SetShellVarContext all
  RMDir /r "$APPDATA\ALICE\toolchain"
  RMDir "$APPDATA\ALICE"
  SetShellVarContext current

  RMDir /r "$INSTDIR"
SectionEnd
