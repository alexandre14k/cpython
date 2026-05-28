myFRpy$target:::function-entry
/copyinstr(arg1) == "start"/
{
    self->trace = 1;
}

myFRpy$target:::gc-start,
myFRpy$target:::gc-done
/self->trace/
{
    printf("%d\t%s:%ld\n", timestamp, probename, arg0);
}

myFRpy$target:::function-return
/copyinstr(arg1) == "start"/
{
    self->trace = 0;
}
