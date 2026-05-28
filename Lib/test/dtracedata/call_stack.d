self int indent;

myFRpy$target:::function-entry
/copyinstr(arg1) == "start"/
{
    self->trace = 1;
}

myFRpy$target:::function-entry
/self->trace/
{
    printf("%d\t%*s:", timestamp, 15, probename);
    printf("%*s", self->indent, "");
    printf("%s:%s:%d\n", basename(copyinstr(arg0)), copyinstr(arg1), arg2);
    self->indent++;
}

myFRpy$target:::function-return
/self->trace/
{
    self->indent--;
    printf("%d\t%*s:", timestamp, 15, probename);
    printf("%*s", self->indent, "");
    printf("%s:%s:%d\n", basename(copyinstr(arg0)), copyinstr(arg1), arg2);
}

myFRpy$target:::function-return
/copyinstr(arg1) == "start"/
{
    self->trace = 0;
}
