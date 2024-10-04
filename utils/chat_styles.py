def get_chat_container_style():
    return """
    <style>
        .message:hover .copy-button {
            visibility: visible;
        }
        .message img{
            max-width: 100%;
            height: auto;
            background-color: #fff;
        }
        .message .codehilite {
            width: 100%;
            overflow-x: auto;
            background-color: #282c34;
            border-radius: 5px;
            margin: 10px 0;
        }
        .message .codehilite pre {
            margin: 0;
            padding: 10px;
            color: #f8f8f2;
        }
        .message .codehilite .hll { background-color: #49483e }
        .message .codehilite .c { color: #75715e } /* Comment */
        .message .codehilite .err { color: #960050; background-color: #1e0010 } /* Error */
        .message .codehilite .k { color: #66d9ef } /* Keyword */
        .message .codehilite .l { color: #ae81ff } /* Literal */
        .message .codehilite .n { color: #f8f8f2 } /* Name */
        .message .codehilite .o { color: #f92672 } /* Operator */
        .message .codehilite .p { color: #f8f8f2 } /* Punctuation */
        .message .codehilite .cm { color: #75715e } /* Comment.Multiline */
        .message .codehilite .cp { color: #75715e } /* Comment.Preproc */
        .message .codehilite .c1 { color: #75715e } /* Comment.Single */
        .message .codehilite .cs { color: #75715e } /* Comment.Special */
        .message .codehilite .ge { font-style: italic } /* Generic.Emph */
        .message .codehilite .gs { font-weight: bold } /* Generic.Strong */
        .message .codehilite .kc { color: #66d9ef } /* Keyword.Constant */
        .message .codehilite .kd { color: #66d9ef } /* Keyword.Declaration */
        .message .codehilite .kn { color: #f92672 } /* Keyword.Namespace */
        .message .codehilite .kp { color: #66d9ef } /* Keyword.Pseudo */
        .message .codehilite .kr { color: #66d9ef } /* Keyword.Reserved */
        .message .codehilite .kt { color: #66d9ef } /* Keyword.Type */
        .message .codehilite .ld { color: #e6db74 } /* Literal.Date */
        .message .codehilite .m { color: #ae81ff } /* Literal.Number */
        .message .codehilite .s { color: #e6db74 } /* Literal.String */
        .message .codehilite .na { color: #a6e22e } /* Name.Attribute */
        .message .codehilite .nb { color: #f8f8f2 } /* Name.Builtin */
        .message .codehilite .nc { color: #a6e22e } /* Name.Class */
        .message .codehilite .no { color: #66d9ef } /* Name.Constant */
        .message .codehilite .nd { color: #a6e22e } /* Name.Decorator */
        .message .codehilite .ni { color: #f8f8f2 } /* Name.Entity */
        .message .codehilite .ne { color: #a6e22e } /* Name.Exception */
        .message .codehilite .nf { color: #a6e22e } /* Name.Function */
        .message .codehilite .nl { color: #f8f8f2 } /* Name.Label */
        .message .codehilite .nn { color: #f8f8f2 } /* Name.Namespace */
        .message .codehilite .nx { color: #a6e22e } /* Name.Other */
        .message .codehilite .py { color: #f8f8f2 } /* Name.Property */
        .message .codehilite .nt { color: #f92672 } /* Name.Tag */
        .message .codehilite .nv { color: #f8f8f2 } /* Name.Variable */
        .message .codehilite .ow { color: #f92672 } /* Operator.Word */
        .message .codehilite .w { color: #f8f8f2 } /* Text.Whitespace */
        .message .codehilite .mf { color: #ae81ff } /* Literal.Number.Float */
        .message .codehilite .mh { color: #ae81ff } /* Literal.Number.Hex */
        .message .codehilite .mi { color: #ae81ff } /* Literal.Number.Integer */
        .message .codehilite .mo { color: #ae81ff } /* Literal.Number.Oct */
        .message .codehilite .sb { color: #e6db74 } /* Literal.String.Backtick */
        .message .codehilite .sc { color: #e6db74 } /* Literal.String.Char */
        .message .codehilite .sd { color: #e6db74 } /* Literal.String.Doc */
        .message .codehilite .s2 { color: #e6db74 } /* Literal.String.Double */
        .message .codehilite .se { color: #ae81ff } /* Literal.String.Escape */
        .message .codehilite .sh { color: #e6db74 } /* Literal.String.Heredoc */
        .message .codehilite .si { color: #e6db74 } /* Literal.String.Interpol */
        .message .codehilite .sx { color: #e6db74 } /* Literal.String.Other */
        .message .codehilite .sr { color: #e6db74 } /* Literal.String.Regex */
        .message .codehilite .s1 { color: #e6db74 } /* Literal.String.Single */
        .message .codehilite .ss { color: #e6db74 } /* Literal.String.Symbol */
        .message .codehilite .bp { color: #f8f8f2 } /* Name.Builtin.Pseudo */
        .message .codehilite .vc { color: #f8f8f2 } /* Name.Variable.Class */
        .message .codehilite .vg { color: #f8f8f2 } /* Name.Variable.Global */
        .message .codehilite .vi { color: #f8f8f2 } /* Name.Variable.Instance */
        .message .codehilite .il { color: #ae81ff } /* Literal.Number.Integer.Long */
        .message-assistant-content, .message-user-content {
            max-width: 100%;
            overflow-wrap: break-word;
            word-break: break-all;
            overflow-x: auto;
        }
        .copy-button {
            visibility: hidden;
            font-size: 1.2em;
            margin: 0 8px;
            border: none;
            border-radius: 5px;
            padding: 2px;
            cursor: pointer;
            background-color: #f8f8f800;
            user-select: none;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
        }
        .copy-button:hover {
            background-color: #f0f0f0;
            transition: all 0.3s;
        }
        .copy-button:active {
            background-color: #e0e0e0;
            transition: all 0.3s;
        }
        .chat-container {
            border: 1px solid #ccc;
            min-height: 10em;
            border-radius: 10px;
            padding: 10px;
            background-color: #f9f9f9;
            overflow-y: scroll;
        }
        .message-user {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 10px;
        }
        .message-user-content {
            background-color: #e0ffe0;
            border-radius: 10px;
            padding: 0 15px;
        }
        .user-avatar {
            background-color: #eee;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-left: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 32px;
        }
        .message-assistant {
            display: flex;
            margin-bottom: 15px;
        }
        .bot-avatar {
            background-color: #eee;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 32px;
        }
        .message-assistant-content {
            background-color: #f0f0f0;
            border-radius: 10px;
            padding: 0 15px;
        }
        .bot-name {
            margin-top: 5px;
            margin-bottom: 10px;
        }
        .tips {
            width: 100%;
            text-align: center;
            color: #bbb;
            user-select: none;
            margin-top: 15px;
            font-size: 0.9em;
            margin-bottom: 20px;
        }
        .message table {
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
        }
        .message th, .message td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .message th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .message tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .message tr:hover {
            background-color: #f5f5f5;
        }
        .code-block {
            position: relative;
            margin: 10px 0;
        }
        .code-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #1e1e1e;
            color: #fff;
            padding: 5px 10px;
            font-family: monospace;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            user-select: none;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
        }
        .code-language {
            font-weight: bold;
        }
        .code-copy-btn {
            background-color: transparent;
            border: 1px solid #fff;
            color: #fff;
            padding: 2px 5px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .code-copy-btn>span {
            user-select: none;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
        }
        .code-copy-btn:hover {
            background-color: #fff;
            color: #1e1e1e;
        }
        .message .codehilite {
            margin-top: 0;
            border-top-left-radius: 0;
            border-top-right-radius: 0;
        }
    </style>
    """